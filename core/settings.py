"""
Django settings — TIFT clone (universitet sayti API + Telegram ariza boti).

Barcha maxfiy va muhitga bog'liq qiymatlar .env dan olinadi (env.example ga qarang).
"""
from datetime import timedelta
from pathlib import Path

from decouple import Csv, config
from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key

from core.ckeditor_config import CKEDITOR_CONFIGS  # noqa: F401  (django-ckeditor o'qiydi)

BASE_DIR = Path(__file__).resolve().parent.parent

# DEBUG: "1"/"True" — yoqiq. Standart: o'chiq.
DEBUG = config('DEBUG', default=False, cast=bool)

SECRET_KEY = config('SECRET_KEY', default='')
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured("SECRET_KEY o'rnatilmagan (production uchun majburiy).")
    SECRET_KEY = get_random_secret_key()

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'ckeditor',
    'drf_yasg',
    'apps.application',
    'apps.common',
    'apps.education',
    'apps.news',
    'apps.telegram',
    'apps.users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': config('SQLITE_PATH', default=str(BASE_DIR / 'db.sqlite3')),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# static/ papkasi bo'lsa qo'shiladi (avval mavjud bo'lmagan papka ko'rsatilgan edi)
STATICFILES_DIRS = [p for p in [BASE_DIR / 'static'] if p.exists()]

# Yuklangan rasmlar (direktor rasmlari va h.k.). Avval MEDIA_ROOT yo'q edi va fayllar
# loyiha ildizidagi images/ ga tushib, git'ga commit bo'lib ketardi.
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Qabul qilingan arizalar shartnomalari (PDF). Ommaga ochiq EMAS — faqat ariza egasi
# API orqali yuklab oladi (application-status/<id>/contract/).
CONTRACT_ROOT = BASE_DIR / 'contracts'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.ScopedRateThrottle'],
    'DEFAULT_THROTTLE_RATES': {
        'auth': config('AUTH_THROTTLE_RATE', default='10/min'),
        'application': config('APPLICATION_THROTTLE_RATE', default='5/min'),
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Frontend boshqa domenda bo'lsa (masalan Netlify), shu ro'yxatga qo'shiladi.
# Lokal ishlashda Vite proxy ishlatiladi va CORS kerak emas.
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:5173', cast=Csv())
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='http://localhost:5173', cast=Csv())

# Telegram bot
BOT_TOKEN = config('BOT_TOKEN', default='')
# Webhook'ni ro'yxatdan o'tkazishda setWebhook(secret_token=...) bilan bir xil qiymat.
# O'rnatilgan bo'lsa, Telegram'dan kelmagan so'rovlar rad etiladi.
TELEGRAM_WEBHOOK_SECRET = config('TELEGRAM_WEBHOOK_SECRET', default='')

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=3600, cast=int)

# django-ckeditor 4 eskirgan; ogohlantirish ma'lum (README ga qarang)
SILENCED_SYSTEM_CHECKS = config('SILENCED_SYSTEM_CHECKS', default='ckeditor.W001', cast=Csv())

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': config('LOG_LEVEL', default='INFO')},
}
