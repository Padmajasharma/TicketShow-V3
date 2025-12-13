# backend/cache/seat_cache.py
"""
Redis-based seat booking cache with atomic operations using Lua scripts.

This module provides a SeatCache class with Lua scripts registered on startup.
If Redis or script registration fails at startup, the instance will provide
safe fallbacks that raise ConnectionError; callers should handle degraded mode.
"""

import logging
from typing import Optional, Dict, List

import redis
try:
    # optional sockets integration
    from sockets import emit_seat_update
except Exception:
    emit_seat_update = None

logger = logging.getLogger(__name__)


class SeatCache:
    """Redis-backed seat cache and atomic reservation helpers."""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)

        # fallback callable used when scripts cannot be registered
        def _scripts_unavailable(*args, **kwargs):
            raise redis.ConnectionError("Redis scripts unavailable")

        def _register(script_text: str):
            try:
                return self.redis.register_script(script_text)
            except Exception as e:
                logger.warning(f"Failed to register redis script: {e}")
                return _scripts_unavailable

        try:
            # Reserve seats (count-based) - returns reservation id and new capacity
            self.reserve_seats_script = _register(r"""
                local show_key = KEYS[1]
                local capacity_key = KEYS[2]
                local lock_key = KEYS[3]
                local requested_seats = tonumber(ARGV[1])
                local lock_timeout = tonumber(ARGV[2])

                if redis.call('SETNX', lock_key, '1') == 0 then
                    return redis.error_reply('LOCK_ACQUISITION_FAILED')
                end

                redis.call('PEXPIRE', lock_key, lock_timeout)

                local current_capacity = tonumber(redis.call('GET', capacity_key) or '0')
                if current_capacity < requested_seats then
                    redis.call('DEL', lock_key)
                    return redis.error_reply('INSUFFICIENT_CAPACITY')
                end

                local new_capacity = current_capacity - requested_seats
                redis.call('SET', capacity_key, tostring(new_capacity))

                local reservation_id = redis.call('INCR', 'reservation_counter')
                local reservation_key = 'reservation:' .. reservation_id
                redis.call('HMSET', reservation_key,
                    'show_id', show_key,
                    'seats_reserved', tostring(requested_seats),
                    'timestamp', redis.call('TIME')[1]
                )
                redis.call('EXPIRE', reservation_key, 300)

                return {reservation_id, new_capacity}
            """)

            # Confirm a reservation and release lock
            self.confirm_booking_script = _register(r"""
                local reservation_key = KEYS[1]
                local lock_key = KEYS[2]
                local booking_key = KEYS[3]
                local user_id = ARGV[1]
                local show_id = ARGV[2]
                local seats = ARGV[3]

                if redis.call('EXISTS', reservation_key) == 0 then
                    return redis.error_reply('RESERVATION_NOT_FOUND')
                end

                redis.call('HMSET', booking_key,
                    'user_id', user_id,
                    'show_id', show_id,
                    'seats', seats,
                    'status', 'confirmed',
                    'timestamp', redis.call('TIME')[1]
                )

                redis.call('DEL', reservation_key)
                redis.call('DEL', lock_key)

                return redis.status_reply('OK')
            """)

            # Release lock and restore capacity
            self.release_lock_script = _register(r"""
                local capacity_key = KEYS[1]
                local lock_key = KEYS[2]
                local reservation_key = KEYS[3]
                local seats_to_restore = tonumber(ARGV[1])

                if redis.call('EXISTS', reservation_key) == 1 then
                    local current_capacity = tonumber(redis.call('GET', capacity_key) or '0')
                    local restored_capacity = current_capacity + seats_to_restore
                    redis.call('SET', capacity_key, tostring(restored_capacity))
                end

                redis.call('DEL', reservation_key)
                redis.call('DEL', lock_key)

                return redis.status_reply('OK')
            """)

            # Hold specific seats (per-seat holds)
            self.hold_seats_script = _register(r"""
                local user_id = ARGV[1]
                local show_id = ARGV[2]
                local ttl = tonumber(ARGV[3])
                local seats = {}
                for i=4, #ARGV do
                    table.insert(seats, ARGV[i])
                end

                local reservation_id = redis.call('INCR', 'reservation_counter')
                local reservation_key = 'reservation:' .. reservation_id
                local set_keys = {}

                for i, seat in ipairs(seats) do
                    local hold_key = 'hold:show:' .. show_id .. ':seat:' .. seat
                    if redis.call('SETNX', hold_key, reservation_id) == 0 then
                        for _, k in ipairs(set_keys) do
                            redis.call('DEL', k)
                        end
                        return redis.error_reply('SEAT_ALREADY_HELD:' .. seat)
                    end
                    redis.call('PEXPIRE', hold_key, ttl * 1000)
                    table.insert(set_keys, hold_key)
                end

                redis.call('HMSET', reservation_key, 'user_id', tostring(user_id), 'show_id', tostring(show_id), 'seats', table.concat(seats, ','), 'timestamp', redis.call('TIME')[1])
                redis.call('EXPIRE', reservation_key, ttl)

                return {tostring(reservation_id), table.concat(seats, ',')}
            """)

            # Confirm seat-level hold
            self.confirm_seat_hold_script = _register(r"""
                local reservation_key = KEYS[1]
                local user_id = ARGV[1]
                local show_id = ARGV[2]

                if redis.call('EXISTS', reservation_key) == 0 then
                    return redis.error_reply('RESERVATION_NOT_FOUND')
                end

                local seats_csv = redis.call('HGET', reservation_key, 'seats') or ''
                local seats = {}
                if seats_csv ~= '' then
                    for seat in string.gmatch(seats_csv, '([^,]+)') do
                        table.insert(seats, seat)
                    end
                end

                for _, seat in ipairs(seats) do
                    local hold_key = 'hold:show:' .. show_id .. ':seat:' .. seat
                    redis.call('DEL', hold_key)
                end

                local booking_key = 'booking:' .. reservation_key:sub(13)
                redis.call('HMSET', booking_key, 'user_id', user_id, 'show_id', show_id, 'seats', seats_csv, 'status', 'confirmed', 'timestamp', redis.call('TIME')[1])

                redis.call('DEL', reservation_key)
                return redis.status_reply('OK')
            """)

            # Release seat-level hold
            self.release_seat_hold_script = _register(r"""
                local reservation_key = KEYS[1]
                if redis.call('EXISTS', reservation_key) == 0 then
                    return redis.status_reply('OK')
                end
                local show_id = redis.call('HGET', reservation_key, 'show_id')
                local seats_csv = redis.call('HGET', reservation_key, 'seats') or ''
                if seats_csv ~= '' then
                    for seat in string.gmatch(seats_csv, '([^,]+)') do
                        local hold_key = 'hold:show:' .. show_id .. ':seat:' .. seat
                        redis.call('DEL', hold_key)
                    end
                end
                redis.call('DEL', reservation_key)
                return redis.status_reply('OK')
            """)

        except Exception as e:
            logger.warning(f"Redis scripts could not be registered at startup: {e}")
            # Safe fallbacks
            self.reserve_seats_script = _scripts_unavailable
            self.confirm_booking_script = _scripts_unavailable
            self.release_lock_script = _scripts_unavailable
            self.hold_seats_script = _scripts_unavailable
            self.confirm_seat_hold_script = _scripts_unavailable
            self.release_seat_hold_script = _scripts_unavailable

    def get_show_capacity(self, show_id: int) -> Optional[int]:
        try:
            capacity = self.redis.get(f"show:{show_id}:capacity")
            return int(capacity) if capacity is not None else None
        except redis.ConnectionError:
            logger.warning("Redis unavailable for capacity check")
            return None

    def set_show_capacity(self, show_id: int, capacity: int) -> bool:
        try:
            return self.redis.set(f"show:{show_id}:capacity", str(capacity))
        except redis.ConnectionError:
            logger.warning("Redis unavailable for capacity update")
            return False

    def reserve_seats_atomic(self, show_id: int, seats_requested: int, lock_timeout_ms: int = 10000) -> Dict:
        try:
            show_key = f"show:{show_id}"
            capacity_key = f"show:{show_id}:capacity"
            lock_key = f"lock:show:{show_id}"

            result = self.reserve_seats_script(keys=[show_key, capacity_key, lock_key], args=[seats_requested, lock_timeout_ms])

            if isinstance(result, list) and len(result) == 2:
                reservation_id, new_capacity = result
                return {'success': True, 'reservation_id': reservation_id, 'new_capacity': new_capacity}
            return {'success': False, 'error': str(result)}

        except redis.ConnectionError:
            logger.warning("Redis unavailable for seat reservation")
            return {'success': False, 'error': 'REDIS_UNAVAILABLE'}
        except Exception as e:
            logger.error(f"Seat reservation failed: {e}")
            return {'success': False, 'error': str(e)}

    def confirm_booking(self, reservation_id: int, user_id: int, show_id: int, seats: int) -> bool:
        try:
            reservation_key = f"reservation:{reservation_id}"
            lock_key = f"lock:show:{show_id}"
            booking_key = f"booking:{reservation_id}"

            result = self.confirm_booking_script(keys=[reservation_key, lock_key, booking_key], args=[user_id, show_id, seats])
            return result == 'OK'

        except redis.ConnectionError:
            logger.warning("Redis unavailable for booking confirmation")
            return False
        except Exception as e:
            logger.error(f"Booking confirmation failed: {e}")
            return False

    def release_lock_and_restore(self, show_id: int, reservation_id: int, seats_to_restore: int) -> bool:
        try:
            capacity_key = f"show:{show_id}:capacity"
            lock_key = f"lock:show:{show_id}"
            reservation_key = f"reservation:{reservation_id}"

            result = self.release_lock_script(keys=[capacity_key, lock_key, reservation_key], args=[seats_to_restore])
            return result == 'OK'

        except redis.ConnectionError:
            logger.warning("Redis unavailable for lock release")
            return False
        except Exception as e:
            logger.error(f"Lock release failed: {e}")
            return False

    def hold_seats(self, user_id: int, show_id: int, seat_list: List[str], ttl_seconds: int = 120) -> Dict:
        try:
            args = [str(user_id), str(show_id), str(ttl_seconds)] + seat_list
            result = self.hold_seats_script(args=args)
            if isinstance(result, list) and len(result) == 2:
                reservation_id = int(result[0])
                seats_csv = result[1]
                seats = seats_csv.split(',') if seats_csv else []
                result = {'success': True, 'reservation_id': reservation_id, 'seats': seats}
                # emit websocket event for held seats
                try:
                    if emit_seat_update:
                            try:
                                logger.info(f"Emitting seat_held for show {show_id}, reservation {reservation_id}, seats={seats}")
                                emit_seat_update(int(show_id), 'seat_held', {'reservation_id': reservation_id, 'seats': seats})
                            except Exception as ee:
                                logger.exception(f"Failed to emit seat_held for reservation {reservation_id}: {ee}")
                except Exception:
                    pass
                return result
            return {'success': False, 'error': str(result)}

        except redis.ConnectionError:
            logger.warning('Redis unavailable for hold seats')
            return {'success': False, 'error': 'REDIS_UNAVAILABLE'}
        except Exception as e:
            logger.error(f'Hold seats failed: {e}')
            return {'success': False, 'error': str(e)}

    def confirm_seat_hold(self, reservation_id: int, user_id: int, show_id: int) -> bool:
        try:
            reservation_key = f'reservation:{reservation_id}'
            result = self.confirm_seat_hold_script(keys=[reservation_key], args=[str(user_id), str(show_id)])
            ok = result == 'OK'
            if ok:
                try:
                    if emit_seat_update:
                        # notify that seats were confirmed (no longer held)
                        # fetch seats from reservation key
                        try:
                            seats_csv = self.redis.hget(reservation_key, 'seats') or ''
                            seats = seats_csv.split(',') if seats_csv else []
                            logger.info(f"Emitting seat_confirmed for show {show_id}, reservation {reservation_id}, seats={seats}")
                            emit_seat_update(int(show_id), 'seat_confirmed', {'reservation_id': reservation_id, 'seats': seats})
                        except Exception as ee:
                            logger.exception(f"Failed to emit seat_confirmed for reservation {reservation_id}: {ee}")
                except Exception:
                    pass
            return ok
        except redis.ConnectionError:
            logger.warning('Redis unavailable for confirm seat hold')
            return False
        except Exception as e:
            logger.error(f'Confirm seat hold failed: {e}')
            return False

    def release_seat_hold(self, reservation_id: int) -> bool:
        try:
            reservation_key = f'reservation:{reservation_id}'
            result = self.release_seat_hold_script(keys=[reservation_key])
            ok = result == 'OK'
            if ok:
                try:
                    if emit_seat_update:
                        # attempt to read show_id and seats from reservation before deletion
                        try:
                            data = self.redis.hgetall(reservation_key)
                            show_id = int(data.get('show_id')) if data.get('show_id') else None
                            seats_csv = data.get('seats') or ''
                            seats = seats_csv.split(',') if seats_csv else []
                            if show_id:
                                logger.info(f"Emitting seat_released for show {show_id}, reservation {reservation_id}, seats={seats}")
                                emit_seat_update(show_id, 'seat_released', {'reservation_id': reservation_id, 'seats': seats})
                        except Exception as ee:
                            logger.exception(f"Failed to emit seat_released for reservation {reservation_id}: {ee}")
                except Exception:
                    pass
            return ok
        except redis.ConnectionError:
            logger.warning('Redis unavailable for release seat hold')
            return False
        except Exception as e:
            logger.error(f'Release seat hold failed: {e}')
            return False

    def get_active_holds(self, show_id: int) -> List[Dict]:
        try:
            pattern = f'hold:show:{show_id}:seat:*'
            keys = self.redis.keys(pattern)
            holds = []
            for k in keys:
                parts = k.split(':')
                seat_id = parts[-1]
                reservation_id = self.redis.get(k)
                if reservation_id:
                    try:
                        res_id = int(reservation_id)
                    except Exception:
                        res_id = reservation_id
                    holds.append({'seat_id': seat_id, 'reservation_id': res_id})
            return holds
        except redis.ConnectionError:
            logger.warning('Redis unavailable for active holds check')
            return []
        except Exception as e:
            logger.error(f'Get active holds failed: {e}')
            return []

    def get_active_reservations(self, show_id: int) -> List[Dict]:
        try:
            pattern = f"reservation:*"
            keys = self.redis.keys(pattern)
            reservations = []
            for key in keys:
                data = self.redis.hgetall(key)
                if data.get('show_id') == str(show_id):
                    reservations.append({
                        'reservation_id': key.split(':')[1],
                        'seats_reserved': int(data.get('seats_reserved', 0)),
                        'timestamp': int(data.get('timestamp', 0))
                    })
            return reservations
        except redis.ConnectionError:
            logger.warning("Redis unavailable for reservations check")
            return []
        except Exception as e:
            logger.error(f"Failed to get reservations: {e}")
            return []

    def cleanup_expired_locks(self) -> int:
        try:
            # Basic cleanup placeholder: returns 0 (no-op). More complex logic
            # should be implemented in production.
            return 0
        except redis.ConnectionError:
            logger.warning("Redis unavailable for cleanup")
            return 0
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return 0

    # Theatre seat map caching helpers
    def get_theatre_seat_map(self, theatre_id: int) -> Optional[List[Dict]]:
        try:
            key = f"theatre:{theatre_id}:seats"
            data = self.redis.get(key)
            if not data:
                return None
            import json
            return json.loads(data)
        except redis.ConnectionError:
            logger.warning('Redis unavailable for theatre seat map get')
            return None
        except Exception as e:
            logger.error(f'Failed to get theatre seat map: {e}')
            return None

    def set_theatre_seat_map(self, theatre_id: int, seat_list: List[Dict]) -> bool:
        try:
            key = f"theatre:{theatre_id}:seats"
            import json
            self.redis.set(key, json.dumps(seat_list))
            return True
        except redis.ConnectionError:
            logger.warning('Redis unavailable for theatre seat map set')
            return False
        except Exception as e:
            logger.error(f'Failed to set theatre seat map: {e}')
            return False

    def delete_theatre_seat_map(self, theatre_id: int) -> bool:
        try:
            key = f"theatre:{theatre_id}:seats"
            self.redis.delete(key)
            return True
        except redis.ConnectionError:
            logger.warning('Redis unavailable for theatre seat map delete')
            return False
        except Exception as e:
            logger.error(f'Failed to delete theatre seat map: {e}')
            return False


# Global instance
seat_cache = SeatCache()

