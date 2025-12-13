import logging
import json
from datetime import datetime
from typing import Optional

from extensions import db
from models import AuditLog

logger = logging.getLogger(__name__)


def log_action(user_id: Optional[int], show_id: Optional[int], ticket_id: Optional[int], action: str, details: Optional[dict] = None):
    """Write an audit log both to the DB (best-effort) and the standard logger.

    This helper swallows DB errors to avoid impacting main request flow.
    """
    payload = details or {}
    try:
        entry = AuditLog(
            user_id=user_id,
            show_id=show_id,
            ticket_id=ticket_id,
            action=action,
            details=json.dumps(payload) if payload else None,
            created_at=datetime.utcnow(),
        )
        db.session.add(entry)
        db.session.commit()
    except Exception as e:
        # Ensure the session is clean after a failed flush/commit so the
        # calling request flow can continue. Do not re-raise - we only
        # attempt best-effort logging.
        try:
            db.session.rollback()
        except Exception:
            # If rollback itself fails, log and continue.
            logger.exception("Failed to rollback DB session after audit log error")
        logger.exception(f"Failed to write audit log to DB: {e}")
    # Always log to application logger as well
    logger.info(f"AUDIT user={user_id} show={show_id} ticket={ticket_id} action={action} details={payload}")
