import os
from pathlib import Path
from datetime import timedelta
import environ
import dj_database_url
from decouple import config


BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

# Security
SECRET_KEY = env("SECRET_KEY", default="django-insecure-change-this")
DEBUG = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

INSTALLED_APPS = [
    # 'daphne',  # REMOVE – incompatible with Python 3.12
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'corsheaders',
    'drf_spectacular',

    'accounts',
    'members',
    'finance',
    'projects',
    'organization',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    # CORS must come BEFORE CommonMiddleware
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    
    # Session middleware must come BEFORE AuthenticationMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    # CSRF protection
    'django.middleware.csrf.CsrfViewMiddleware',
    
    # Authentication - relies on session middleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'GNET.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'GNET.wsgi.application'

# Database (Neon)
DATABASES = {
    'default': dj_database_url.config(
        default=env("DATABASE_URL"),
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True
    )
}

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mulishem2002@gmail.com'
EMAIL_HOST_PASSWORD = 'xhzisxxodysphumy'  # No spaces
DEFAULT_FROM_EMAIL = 'mulishem2002@gmail.com'
FRONTEND_URL = 'http://localhost:5173'

# User model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================================
# AUTHENTICATION CONFIGURATION - MIGRATED FROM JWT TO SESSION
# ============================================================================

# JWT Configuration (COMMENTED OUT - Switched to session auth for better security)
# SIMPLE_JWT = {
#     'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
#     'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
#     'ALGORITHM': 'HS256',
#     'SIGNING_KEY': SECRET_KEY,
#     'AUTH_HEADER_TYPES': ('Bearer',),
# }

# Django REST Framework Configuration
REST_FRAMEWORK = {
    # CHANGED: Using SessionAuthentication instead of JWT
    # SessionAuthentication uses HTTP-only cookies which are MORE SECURE
    # - Cookies cannot be accessed by JavaScript (prevents XSS attacks)
    # - Automatically sent with every request (no manual token management)
    # - Built-in CSRF protection
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',  # ✅ Secure cookie-based auth
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',  # ❌ Removed JWT
    ),
    
    # All API endpoints require authentication by default
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    
    # API documentation schema
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ============================================================================
# CORS (Cross-Origin Resource Sharing) Configuration
# ============================================================================

# SECURITY NOTE: In production, NEVER use CORS_ALLOW_ALL_ORIGINS = True
# For development, we'll allow specific origins instead:
CORS_ALLOW_ALL_ORIGINS = False  # ✅ Changed from True for better security

# Explicitly allow your frontend origin
# This tells Django which domains can make authenticated requests to your API
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",      # Vite default dev server
    "http://127.0.0.1:5173",      # Alternative localhost
    "http://localhost:3000",      # React/Next.js default
    "http://127.0.0.1:3000",      # Alternative localhost
]

# CRITICAL: Allow cookies/credentials to be sent with cross-origin requests
# Without this, session cookies won't be sent from your frontend to backend
CORS_ALLOW_CREDENTIALS = True  # ✅ Required for session auth to work

# Allow these HTTP methods from the frontend
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Allow these headers in requests from frontend
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',      # ✅ Required for CSRF protection
    'x-requested-with',
]

# ============================================================================
# SESSION CONFIGURATION - The Authentication Cookie Settings
# ============================================================================

# Session cookie name (this is the authentication cookie)
SESSION_COOKIE_NAME = 'sessionid'

# HTTP-ONLY: JavaScript CANNOT access this cookie (prevents XSS attacks)
# This is why session auth is more secure than localStorage tokens
SESSION_COOKIE_HTTPONLY = True  # ✅ CRITICAL for security

# SameSite: Controls when cookies are sent with cross-site requests
# 'Lax' = Cookie sent with top-level navigation (good balance of security & usability)
# 'Strict' = Never sent with cross-site requests (more secure but can break things)
# 'None' = Always sent (requires SECURE=True, only for production with HTTPS)
SESSION_COOKIE_SAMESITE = 'Lax'  # ✅ Good for development

# SECURE: Only send cookie over HTTPS
# Must be False in development (since we use HTTP), True in production
SESSION_COOKIE_SECURE = False  # ✅ Set to True in production with HTTPS

# How long the session lasts (in seconds)
# 1209600 seconds = 14 days
SESSION_COOKIE_AGE = 1209600

# Domain for the session cookie
# None = Cookie only works on current domain
SESSION_COOKIE_DOMAIN = None

# Path for the session cookie
SESSION_COOKIE_PATH = '/'

# Whether to save session on every request (False = better performance)
SESSION_SAVE_EVERY_REQUEST = False

# Whether session expires when browser closes
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# ============================================================================
# CSRF (Cross-Site Request Forgery) PROTECTION
# ============================================================================

# CSRF cookie name (this is a separate cookie from session)
CSRF_COOKIE_NAME = 'csrftoken'

# HTTP-ONLY: Must be False so frontend JavaScript can READ this cookie
# Frontend needs to read this cookie and send it back in X-CSRFToken header
CSRF_COOKIE_HTTPONLY = False  # ✅ Frontend needs to access this

# SameSite setting for CSRF cookie (same as session)
CSRF_COOKIE_SAMESITE = 'Lax'

# SECURE: Only send over HTTPS (False for development)
CSRF_COOKIE_SECURE = False  # ✅ Set to True in production with HTTPS

# Path for CSRF cookie
CSRF_COOKIE_PATH = '/'

# Domain for CSRF cookie
CSRF_COOKIE_DOMAIN = None

# Which origins are trusted for CSRF-protected requests
# This must match your CORS_ALLOWED_ORIGINS
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Whether to use the X-CSRFToken header (modern approach)
CSRF_USE_SESSIONS = False

# Header name that frontend sends CSRF token in
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'

# ============================================================================
# PRODUCTION SECURITY CHECKLIST
# ============================================================================

# When deploying to production, change these:
if not DEBUG:
    # Enable HTTPS-only cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Stricter CORS - only allow your production domain
    CORS_ALLOWED_ORIGINS = [
        "https://yourdomain.com",
    ]
    
    # Add your production domain to trusted origins
    CSRF_TRUSTED_ORIGINS = [
        "https://yourdomain.com",
    ]
    
    # Enable security headers
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    
    # Strict transport security
    SESSION_COOKIE_SAMESITE = 'Strict'
    CSRF_COOKIE_SAMESITE = 'Strict'

# ============================================================================
# API DOCUMENTATION
# ============================================================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'G-NET Backend API',
    'DESCRIPTION': 'Generational Entrepreneurs Network API',
    'VERSION': '1.0.0',
}