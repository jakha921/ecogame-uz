"""Production settings."""

import environ

from .base import *  # noqa: F401, F403

env = environ.Env()

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = False
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["ecogame.fullfocus.dev"])

DATABASES = {"default": env.db("DATABASE_URL")}

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["https://ecogame.fullfocus.dev"])

GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID", default="")

# Security settings for production
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False  # Handled by nginx/Coolify
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
