from pathlib import Path
import os

import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-@o@qevtn-nr+4#k3nq_-aejf7q5hnwj6=2n^jga3maal6s4chf')

# Lokalda True, Vercel'da (VERCEL env mavjud) False. DEBUG=1/0 bilan qo'lda o'zgartirish mumkin.
DEBUG = os.environ.get('DEBUG', '0' if os.environ.get('VERCEL') else '1') == '1'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.vercel.app',
    '.now.sh',
]

CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'https://*.now.sh',
]

# Vercel proxy orqali HTTPS so'rovlarni to'g'ri aniqlash uchun
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'portfolio',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates/'],
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# DATABASE_URL berilsa (Supabase Postgres) o'sha ishlatiladi, aks holda lokal SQLite.
# Vercel'da SQLite faqat o'qish uchun, admin'dan saqlash uchun Postgres kerak.
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=0,
    )
}
if DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
    DATABASES['default'].setdefault('OPTIONS', {}).update({
        'sslmode': 'require',
        # Supabase pooler (transaction mode) prepared statement'larni qo'llamaydi
        'prepare_threshold': None,
    })
    DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True


# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles_build' / 'static'

_extra_static = BASE_DIR / 'portfolio' / 'static'
STATICFILES_DIRS = [_extra_static] if _extra_static.exists() else []

# Vercel'da collectstatic ishlamaydi, shuning uchun WhiteNoise fayllarni to'g'ridan-to'g'ri app papkalaridan beradi
WHITENOISE_USE_FINDERS = True

# Admin'dan yuklangan fayllar: Supabase sozlangan bo'lsa o'sha yerga, aks holda media/ papkaga
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')
SUPABASE_BUCKET = os.environ.get('SUPABASE_BUCKET', 'media')

STORAGES = {
    'default': {
        'BACKEND': 'portfolio.storage.SupabaseStorage'
        if SUPABASE_URL and SUPABASE_SERVICE_KEY
        else 'django.core.files.storage.FileSystemStorage'
    },
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Email: kontakt formasidan kelgan xabarlar shu pochtaga yuboriladi.
# EMAIL_HOST_PASSWORD - Gmail "App password" (oddiy parol emas).
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 10
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'nuriddinovu79@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', EMAIL_HOST_USER)
