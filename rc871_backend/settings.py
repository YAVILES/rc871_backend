"""
Django settings for rc871_backend project.

Generated by 'django-admin startproject' using Django 3.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
from datetime import timedelta
import environ
from money.currency import Currency

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, True),
    MEDIA_URL=(str, 'http://localhost:8000/media'),
    WEB_URL=(str, 'https://localhost'),
    SITE_VERSION=(str, 'v0.1'),
    SITE_LOGO=(str, 'https://localhost/image/logo.png'),
    SITE_NAME=(str, 'B2B'),
    SECRET_KEY=(str, '4)!6(7cj4wfibai#r%qk=o51ba-(^c-cevex_5e-3hr@4a8kr1'),
    DATABASE=(str, 'rc871_backend'),
    DATABASE_USER=(str, 'postgres'),
    DATABASE_PASSWORD=(str, 'postgres'),
    DATABASE_HOST=(str, 'localhost'),
    DATABASE_PORT=(int, 5432),
    TIME_ZONE=(str, 'America/Caracas'),
    EMAIL_PASSWORD=(str, 'passEmail'),
    EMAIL_HOST_USER=(str, "example@gmail.com"),
    EMAIL_HOST=(str, 'smtp.googlemail.com'),
    EMAIL_PORT=(int, 587),
    PREFIX_APP=(str, 'btp'),
)

# reading .env file
environ.Env.read_env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '194.163.161.64']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',

    # Vendor
    'rest_framework',
    'corsheaders',
    'django_celery_beat',
    'django_celery_results',
    'whitenoise',
    'drf_yasg2',
    'django_extensions',
    'django_filters',
    'constance',
    'constance.backends.database',
    'sequences',
    'django_ace',
    'fcm_django',
    'auditlog',
    'import_export',
    'multiselectfield',
    'channels',
    #  'sslserver',
    #  'debug_toolbar',

    # RC871
    'apps.core.apps.CoreConfig',
    'apps.security.apps.SecurityConfig',
    'apps.system.apps.SystemConfig',
    'apps.payment.apps.PaymentConfig',
    'apps.chat.apps.ChatConfig',
]

MIDDLEWARE = [
    #  'debug_toolbar.middleware.DebugToolbarMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'rc871_backend.middleware.RestAuthMiddleware',
    'auditlog.middleware.AuditlogMiddleware',
]

ROOT_URLCONF = 'rc871_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'rc871_backend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': env('DATABASE'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
        'HOST': env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT'),
        'OPTIONS': {
            'connect_timeout': 5,
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

"""
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
"""

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = env('TIME_ZONE')

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_URL = env('MEDIA_URL')

# MEDIA_ROOT = '/var/www/html/admin871/media/'  # os.path.join(BASE_DIR, "media")
MEDIA_ROOT = 'C:/xampp/htdocs/admin871/media/'

AUTH_USER_MODEL = 'security.User'
AUTHENTICATION_BACKENDS = ['apps.security.backends.CustomAuthenticationBackend', ]

WEB_URL = env('WEB_URL')

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(hours=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

SITE_NAME = env('SITE_NAME')
SITE_LOGO = env('SITE_LOGO')
SITE_VERSION = env('SITE_VERSION')

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with'
]

CURRENCY = Currency.USD
CURRENCY_FORMAT = '$'
CURRENCY_CHANGE = Currency.VEF
CURRENCY_CHANGE_FORMAT = 'Bs'

EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_PASSWORD')
EMAIL_USE_TLS = True

FCM_DJANGO_SETTINGS = {
    "APP_VERBOSE_NAME": "btp",
    # true if you want to have only one active device per registered user at a time
    # default: False
    "ONE_DEVICE_PER_USER": False,
    # devices to which notifications cannot be sent,
    # are deleted upon receiving error response from FCM
    # default: False
    "DELETE_INACTIVE_DEVICES": False,
}

# Config Import Export
IMPORT_EXPORT_USE_TRANSACTIONS = True
IMPORT_EXPORT_IMPORT_PERMISSION_CODE = 'change'

CONSTANCE_CONFIG = {
    #'IVA': (12.00, "Impuesto al Valor Agregado (IVA)", float),
    'CHANGE_FACTOR': (0, "Factor de cambio Bs", float),
    'ADVISER_DEFAULT_ID': (None, "Asesor por Defecto", str),
}

# CELERY STUFF
BROKER_URL = 'redis://localhost:6379/'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

ASGI_APPLICATION = "rc871_backend.asgi.application"

INTERNAL_IPS = [
    '127.0.0.1',
    '194.163.161.64'
]

# HTTPS:
# USE_X_FORWARDED_HOST = True
#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
#SECURE_HSTS_PRELOAD = True
#SECURE_HSTS_INCLUDE_SUBDOMAINS = True

TIMEOUT = None
