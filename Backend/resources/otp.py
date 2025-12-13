import os
import random
import logging
import json
from typing import Optional

from flask_restful import Resource
from flask import request
from flask_jwt_extended import create_access_token

import smtplib
from email.mime.text import MIMEText

try:
    from twilio.rest import Client as TwilioClient
except Exception:
    TwilioClient = None

import redis

from extensions import db
from models import User

logger = logging.getLogger(__name__)


def _redis_client():
    url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    try:
        return redis.from_url(url, decode_responses=True)
    except Exception:
        return None


def _send_email(to_email: str, subject: str, body: str) -> bool:
    # Support multiple env var names so common dev setups work (SMTP_HOST for .env,
    # but Config often exposes SMTP_SERVER). Fall back to either name.
    host = os.environ.get("SMTP_HOST") or os.environ.get("SMTP_SERVER")
    port = int(os.environ.get("SMTP_PORT") or os.environ.get("MAIL_PORT") or 587)
    user = os.environ.get("SMTP_USERNAME") or os.environ.get("MAIL_USERNAME")
    pwd = os.environ.get("SMTP_PASSWORD") or os.environ.get("MAIL_PASSWORD")
    sender = os.environ.get("EMAIL_FROM") or user

    if not host or not sender:
        logger.warning("SMTP not configured (looked for SMTP_HOST/SMTP_SERVER and EMAIL_FROM/SMTP_USERNAME)")
        return False

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email

    try:
        logger.info(f"Attempting to send OTP email to {to_email} via SMTP {host}:{port} (sender={sender})")
        server = smtplib.SMTP(host, port, timeout=10)
        # If SMTP_DEBUG=1 is set in env, enable smtplib debug output (goes to stderr/server.log)
        try:
            if os.environ.get('SMTP_DEBUG', '0') == '1':
                server.set_debuglevel(1)
        except Exception:
            pass
        try:
            server.starttls()
        except Exception as e_starttls:
            # STARTTLS may not be supported by dev SMTP servers; log and continue
            logger.debug(f"STARTTLS failed or not supported: {e_starttls}")

        if user and pwd:
            try:
                server.login(user, pwd)
            except Exception as e_login:
                # Log exception and also print a short message to stderr so it appears in simple server logs
                logger.exception(f"SMTP login failed: {e_login}")
                try:
                    # also print minimal info to stderr for immediate visibility
                    import sys
                    print(f"SMTP login failed: {e_login}", file=sys.stderr)
                except Exception:
                    pass
                # continue to attempt send without raising to allow non-auth SMTP servers

        server.sendmail(sender, [to_email], msg.as_string())
        server.quit()
        logger.info(f"OTP email sent to {to_email} (via {host}:{port})")
        return True
    except Exception as e:
        logger.exception(f"Failed to send OTP email: {e}")
        return False


def _send_sms_via_twilio(to_number: str, body: str) -> bool:
    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("TWILIO_FROM_NUMBER")

    if not TwilioClient or not sid or not token or not from_number:
        logger.warning("Twilio not configured or client missing")
        return False

    try:
        client = TwilioClient(sid, token)
        client.messages.create(body=body, from_=from_number, to=to_number)
        return True
    except Exception as e:
        logger.exception(f"Failed to send SMS via Twilio: {e}")
        return False


class OtpService:
    def __init__(self):
        self.redis = _redis_client()

    def _otp_key(self, identifier: str) -> str:
        return f"otp:{identifier}"

    def _attempts_key(self, identifier: str) -> str:
        return f"otp:attempts:{identifier}"

    def generate_and_store(self, identifier: str, ttl: int = 300) -> str:
        code = f"{random.randint(0, 999999):06d}"
        try:
            if self.redis:
                self.redis.set(self._otp_key(identifier), code, ex=ttl)
                self.redis.set(self._attempts_key(identifier), 0, ex=ttl)
            else:
                # best-effort in-memory fallback (not durable)
                logger.warning("Redis not available for OTP storage")
        except Exception as e:
            logger.exception(f"Failed to store OTP in redis: {e}")
        return code

    def verify(self, identifier: str, code: str, max_attempts: int = 5) -> bool:
        try:
            if not self.redis:
                logger.warning("Redis not available for OTP verify")
                return False

            attempts = int(self.redis.get(self._attempts_key(identifier) or 0))
            if attempts >= max_attempts:
                return False

            stored = self.redis.get(self._otp_key(identifier))
            if not stored:
                return False

            if str(stored) == str(code):
                # success: delete keys
                self.redis.delete(self._otp_key(identifier))
                self.redis.delete(self._attempts_key(identifier))
                return True
            else:
                self.redis.incr(self._attempts_key(identifier))
                return False
        except Exception as e:
            logger.exception(f"OTP verification failed: {e}")
            return False


otp_service = OtpService()


class SendOtpResource(Resource):
    def post(self):
        data = request.get_json() or {}
        identifier = data.get("identifier")  # email or phone
        via = data.get("via", "email")

        if not identifier:
            return {"message": "identifier (email or phone) is required"}, 400

        code = otp_service.generate_and_store(identifier)
        logger.info(f"Generated OTP for identifier={identifier} (will store in redis key otp:{identifier})")
        body = f"Your verification code is: {code}\nThis code will expire in 5 minutes."

        success = False
        if via == "email":
            success = _send_email(identifier, "Your OTP code", body)
        elif via == "sms":
            success = _send_sms_via_twilio(identifier, body)
        else:
            return {"message": "Invalid 'via' value, use 'email' or 'sms'"}, 400

        if not success:
                # In development it can be useful to return the OTP directly when SMTP/Twilio
                # is not configured. This is explicitly gated by the DEV_RETURN_OTP env var
                # to avoid leaking codes in production.
                if os.environ.get('DEV_RETURN_OTP', '0') == '1':
                    logger.warning('Delivery failed but DEV_RETURN_OTP=1; returning OTP in response for dev')
                    return {"message": "OTP sent (dev)", "otp": code}, 200
                # Also log current SMTP env vars for debugging (do not log secrets)
                logger.info(f"SMTP configuration used: SMTP_HOST={os.environ.get('SMTP_HOST')}, SMTP_SERVER={os.environ.get('SMTP_SERVER')}, SMTP_PORT={os.environ.get('SMTP_PORT')}, MAIL_PORT={os.environ.get('MAIL_PORT')}")
                return {"message": "Failed to deliver OTP (check SMTP/Twilio configuration)"}, 503

        return {"message": "OTP sent"}, 200


class VerifyOtpResource(Resource):
    def post(self):
        data = request.get_json() or {}
        identifier = data.get("identifier")
        code = data.get("code")

        if not identifier or not code:
            return {"message": "identifier and code are required"}, 400

        ok = otp_service.verify(identifier, code)
        if not ok:
            return {"message": "Invalid or expired code"}, 400

        # OTP verified — create or return token for user (email flows)
        user = User.query.filter_by(email=identifier).first()
        if not user:
            # Auto-create a user for email-based verification (no password)
            user = User(username=identifier.split("@")[0], email=identifier)
            # mark active, no password set — encourage complete signup later
            user.active = True
            db.session.add(user)
            db.session.commit()

        token = create_access_token(identity=user.username, additional_claims={"is_admin": user.is_admin})
        return {"message": "verified", "token": token}, 200
