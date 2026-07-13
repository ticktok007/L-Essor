"""
Production settings — Campus Innovation & Engagement Intelligence Hub
Imports base settings and enforces security defaults.
"""
from decouple import config
from .base import *  # noqa: F401, F403

DEBUG = False

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    cast=lambda v: [s.strip() for s in v.split(",")],
)

# ── Security hardening ────────────────────────────────────────────────────────
SECURE_SSL_REDIRECT              = True
SECURE_HSTS_SECONDS              = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS   = True
SECURE_HSTS_PRELOAD              = True
SESSION_COOKIE_SECURE            = True
CSRF_COOKIE_SECURE               = True
SECURE_BROWSER_XSS_FILTER        = True
SECURE_CONTENT_TYPE_NOSNIFF      = True
X_FRAME_OPTIONS                  = "DENY"

# ── Static / media ────────────────────────────────────────────────────────────
# Configure STATIC_ROOT and a CDN or WhiteNoise for production serving.