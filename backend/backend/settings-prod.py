"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 1.11.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import socket

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'dta0wk@%ss$$&l34j*+yw19v1jjr!n@670(zn_it5#+ocsby5q'
if os.path.exists('/run/secrets/secret-key'):
    with open('/run/secrets/secret-key') as f:
        SECRET_KEY = f.read().strip()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', socket.gethostname(), 'localhost', 'backend']
if os.path.exists('/run/secrets/allowed-hosts'):
    with open('/run/secrets/allowed-hosts') as f:
        ALLOWED_HOSTS = f.read().strip().split(',')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework.authtoken',
    'django_celery_beat',
    'django_filters',
    'rest_framework',
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_WHITELIST = (
    'localhost:3000',
    '127.0.0.1:3000',
)
if os.path.exists('/run/secrets/cors-origin-whitelist'):
    with open('/run/secrets/cors-origin-whitelist') as f:
        CORS_ORIGIN_WHITELIST = [x.strip() for x in f.read().split('\n')]


ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

with open('/run/secrets/mysql-user') as f:
    mysql_user = f.read().strip()
with open('/run/secrets/mysql-password') as f:
    mysql_password = f.read().strip()

DATABASES = {
    #'default': {
    #    'ENGINE': 'django.db.backends.sqlite3',
    #    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    #}
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'backend',
        'USER': mysql_user,
        'PASSWORD': mysql_password,
        'HOST': 'mysql',
        'PORT': '3306',
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)
STATIC_ROOT = '/www/data/static/'
if os.path.exists('/run/secrets/static-root'):
    with open('/run/secrets/static-root') as f:
        STATIC_ROOT = f.read().strip()

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '10000000/day'
    },
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.Pagination',
    'PAGE_SIZE': 10
}

# db connections
CONN_MAX_AGE = 20

BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = False
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

MONGODB_SERVER = "mongodb"
MONGODB_PORT = 27017
MONGODB_DB = "used_car"
MONGODB_RAW_POSTS = "sfbay_redis"
MONGODB_TRAIN_POSTS = "sfbay_train"
MONGODB_D3_TASK = "sfbay_d3_task"

APP_SCHEME = 'http'
APP_HOST = 'backend'
APP_PORT = 8000
APP_STATIC_DIR = STATIC_ROOT if not DEBUG else os.path.join(BASE_DIR, "static")

APP_WORKER_TOKEN = ''
if os.path.exists('/run/secrets/app-worker-token'):
    with open('/run/secrets/app-worker-token') as f:
        APP_WORKER_TOKEN = f.read().strip()

WORKER_D3_TASK_DISPATCH_PERIOD = 3600

MIN_YEAR = 1990