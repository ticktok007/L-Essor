"""
Development settings — Campus Innovation & Engagement Intelligence Hub
Imports base settings and enables debug mode.
"""
from decouple import config
from .base import *  # noqa: F401, F403

DEBUG = config("DEBUG", default=True, cast=bool)

# Allow all hosts locally for convenience
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="127.0.0.1,localhost",
    cast=lambda v: [s.strip() for s in v.split(",")],
)

# Verbose logging in dev
LOGGING = {
    "version":            1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level":    "DEBUG",
    },
}

REST_FRAMEWORK.update({
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
})

import sys
if 'spectacular' in sys.argv:
    print(f"DEBUG: Schema Class is {REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS']}")
