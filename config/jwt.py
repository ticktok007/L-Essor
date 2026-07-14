"""
config/jwt.py
Campus Innovation & Engagement Intelligence Hub
SIMPLE_JWT configuration — imported into campushub/settings/base.py
"""

from datetime import timedelta

SIMPLE_JWT = {
    # Token lifetimes
    "ACCESS_TOKEN_LIFETIME":  timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    # Rotation / blacklisting — disabled for Phase 2
    "ROTATE_REFRESH_TOKENS":   False,
    "BLACKLIST_AFTER_ROTATION": False,

    # Signing
    "ALGORITHM":              "HS256",
    "SIGNING_KEY":            None,   # falls back to Django SECRET_KEY
    "VERIFYING_KEY":          None,
    "AUDIENCE":               None,
    "ISSUER":                 None,

    # Auth header
    "AUTH_HEADER_TYPES":      ("Bearer",),
    "AUTH_HEADER_NAME":       "HTTP_AUTHORIZATION",

    # User identity
    "USER_ID_FIELD":          "id",
    "USER_ID_CLAIM":          "user_id",

    # Token classes
    "AUTH_TOKEN_CLASSES":     ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM":       "token_type",

    # Sliding tokens — not used
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM":    "refresh_exp",
    "SLIDING_TOKEN_LIFETIME":             timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME":     timedelta(days=1),

    # Custom serializer — adds role + full_name to token response
    "TOKEN_OBTAIN_SERIALIZER":
        "apps.accounts.api.serializers.CustomTokenObtainPairSerializer",
}