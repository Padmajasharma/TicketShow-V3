"""Socket helpers for broadcasting seat events to connected clients.

This module exposes `init_socketio(app)` which returns a `SocketIO` instance
and `emit_seat_update(show_id, event_type, payload)` for other modules to call.
"""
from typing import Optional
import logging

socketio = None
logger = logging.getLogger(__name__)


def init_socketio(app):
    """Initialize and return a SocketIO instance tied to the Flask `app`.

    Use `eventlet` or `gevent` in production. CORS allowed for frontend.
    """
    global socketio
    try:
        from flask_socketio import SocketIO
    except Exception:
        logger.warning("flask_socketio not installed; websocket disabled")
        return None

    # Prefer eventlet, then gevent, otherwise fall back to threading so the
    # server can still run without extra async driver packages installed.
    async_mode = None
    try:
        import eventlet  # noqa: F401
        async_mode = 'eventlet'
    except Exception:
        try:
            import gevent  # noqa: F401
            async_mode = 'gevent'
        except Exception:
            async_mode = 'threading'

    logger.info(f"Initializing SocketIO with async_mode={async_mode}")
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode=async_mode)

    @socketio.on('join')
    def _on_join(data):
        # data: { 'show_id': 123 }
        show_id = data.get('show_id')
        if show_id:
            room = f"show_{show_id}"
            try:
                from flask_socketio import join_room
                join_room(room)
            except Exception:
                pass

    @socketio.on('leave')
    def _on_leave(data):
        show_id = data.get('show_id')
        if show_id:
            room = f"show_{show_id}"
            try:
                from flask_socketio import leave_room
                leave_room(room)
            except Exception:
                pass

    return socketio


def emit_seat_update(show_id: int, event_type: str, payload: dict, room: Optional[str] = None):
    """Emit a seat-related update to clients listening for the given show.

    - `event_type` is a short string like 'seat_held' | 'seat_released' | 'seat_confirmed'.
    - `payload` contains event-specific data.
    """
    global socketio
    if not socketio:
        return
    try:
        event_name = 'seat_update'
        data = {'show_id': show_id, 'type': event_type, 'data': payload}
        target_room = room or f"show_{show_id}"
        socketio.emit(event_name, data, room=target_room)
    except Exception as e:
        logger.exception(f"Failed to emit seat update: {e}")
