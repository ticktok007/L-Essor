"""
Paste into settings/base.py — Campus Innovation & Engagement Intelligence Hub
PostgreSQL + pgvector configuration (Phase 2).
"""
import environ

env = environ.Env(
    DATABASE_NAME=(str, "campushub"),
    DATABASE_USER=(str, "campushub"),
    DATABASE_PASSWORD=(str, "campushub"),
    DATABASE_HOST=(str, "localhost"),
    DATABASE_PORT=(int, 5432),
)

# Replace the SQLite DATABASES block with:
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DATABASE_NAME"),
        "USER": env("DATABASE_USER"),
        "PASSWORD": env("DATABASE_PASSWORD"),
        "HOST": env("DATABASE_HOST"),
        "PORT": env("DATABASE_PORT"),
        "OPTIONS": {
            "options": "-c search_path=public",
        },
    }
}

# Add to INSTALLED_APPS (pgvector Django integration):
# INSTALLED_APPS += ["pgvector"]

# Startup model usage:
# from pgvector.django import VectorField, CosineDistance
