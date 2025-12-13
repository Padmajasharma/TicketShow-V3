from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from cache.seat_cache import seat_cache
from utils.audit import log_action
from models import User


class SeatHoldResource(Resource):
    @jwt_required()
    def post(self, show_id):
        data = request.get_json() or {}
        seats = data.get('seats', [])
        ttl = int(data.get('ttl_seconds', 120))

        if not seats or not isinstance(seats, list):
            return {'message': 'seats must be a non-empty list of seat ids (e.g. ["A1","A2"])'}, 400

        current_user = get_jwt_identity()
        try:
            # Log user clicked seat(s)
            try:
                user_obj = User.query.filter_by(username=current_user).first()
                user_id = user_obj.id if user_obj else None
            except Exception:
                user_id = None
            try:
                log_action(user_id, show_id, None, 'seat_clicked', {'seats': seats})
            except Exception:
                pass
            # seat_cache.hold_seats expects a numeric user id if that's how system stores it
            # Here we pass the username/identity; backend can use numeric ids if preferred
            res = seat_cache.hold_seats(current_user, show_id, seats, ttl_seconds=ttl)
            if not res.get('success'):
                try:
                    log_action(user_id, show_id, None, 'seat_lock_failed', {'error': res.get('error')})
                except Exception:
                    pass
                return {'message': res.get('error', 'Failed to hold seats')}, 409
            # Log seat locked
            try:
                log_action(user_id, show_id, None, 'seat_locked', {'reservation_id': res.get('reservation_id'), 'seats': res.get('seats')})
            except Exception:
                pass

            return {
                'reservation_id': res['reservation_id'],
                'seats': res['seats'],
                'ttl_seconds': ttl
            }, 201
        except Exception as e:
            return {'message': f'Error holding seats: {e}'}, 500


class SeatHoldReleaseResource(Resource):
    @jwt_required()
    def delete(self, show_id, reservation_id):
        current_user = get_jwt_identity()
        try:
            # Verify reservation owner if possible
            reservation_key = f'reservation:{reservation_id}'
            owner = seat_cache.redis.hget(reservation_key, 'user_id')
            if owner and str(owner) != str(current_user):
                return {'message': 'Not authorized to release this reservation'}, 403

            ok = seat_cache.release_seat_hold(reservation_id)
            if ok:
                return {'message': 'Released hold'}, 200
            else:
                return {'message': 'Failed to release hold'}, 500
        except Exception as e:
            return {'message': f'Error releasing hold: {e}'}, 500
