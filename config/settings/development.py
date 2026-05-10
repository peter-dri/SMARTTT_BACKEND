from .base import *  # noqa: F403,F401
import os

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Use SQLite for development if POSTGRES_PASSWORD env var is not set
if not os.getenv("POSTGRES_PASSWORD"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
