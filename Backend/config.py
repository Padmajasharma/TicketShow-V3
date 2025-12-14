# backend/config.py
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Core secrets and DB
    SECRET_KEY = os.getenv("SECRET_KEY", "5e14a40fcda83b6d909ff639f40cccb4")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "sqlite:///" + os.path.join(basedir, "site.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)

    UPLOAD_FOLDER = os.path.join(basedir, "static", "uploads")

    # Mail config - prefer environment variables for credentials/secrets
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() in ("1", "true", "yes")
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False").lower() in ("1", "true", "yes")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")

    # Celery / Redis - now all can be set via env
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
    CELERY_WORKER_CONCURRENCY = int(os.getenv("CELERY_WORKER_CONCURRENCY", 4))

    # Cache
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL", "redis://localhost:6379/0")

    # SMTP settings used by lower-level tasks/clients. These fall back to
    # the MAIL_* settings when a separate SMTP_* value is not provided.
    SMTP_SERVER = os.getenv("SMTP_SERVER", MAIL_SERVER)
    SMTP_PORT = int(os.getenv("SMTP_PORT", MAIL_PORT))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", MAIL_USERNAME)
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", MAIL_PASSWORD)

    # Feature flags for progressive rollout. Can be overridden in environment.
    FEATURE_FLAGS = {
        "recommendations": os.getenv("FEATURE_RECOMMENDATIONS", "True").lower() in ("1", "true", "yes"),
        # Enable websocket updates by default in development so Socket.IO is mounted
        "websocket_updates": os.getenv("FEATURE_WEBSOCKET_UPDATES", "True").lower() in ("1", "true", "yes"),
    }
