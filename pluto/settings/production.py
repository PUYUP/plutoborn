import sys

from .base import *
from .project import *

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

DEBUG = True
ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1', 
    '[::1]', 
    'pluto-tryout.herokuapp.com', 
    '103.41.206.67',
    'tryout.moorid.com'
]


# Sentry
sentry_sdk.init(
    dsn="https://4e67ab469e844d3eb9d4aa5f71a97dba@o400235.ingest.sentry.io/5258558",
    integrations=[DjangoIntegration()],

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)


# Django Sessions
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/2.2/ref/settings/
# SESSION_COOKIE_SECURE = True
# SESSION_COOKIE_SAMESITE = None
# SESSION_COOKIE_HTTPONLY = True

# SECURE_REFERRER_POLICY = 'same-origin'
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_SSL_REDIRECT = True
# SECURE_HSTS_SECONDS = 5
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# X_FRAME_OPTIONS = 'DENY'


# Django csrf
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/2.2/ref/csrf/
CSRF_COOKIE_SECURE = False
# CSRF_TRUSTED_ORIGINS = [
#     'opsional001.firebaseapp.com'
# ]


# Django CORS
# ------------------------------------------------------------------------------
# https://pypi.org/project/django-cors-headers/
CORS_ALLOW_CREDENTIALS = True
# CORS_ORIGIN_WHITELIST = [
#     'https://opsional001.firebaseapp.com'
# ]


# Static files (CSS, JavaScript, Images)
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_PATH, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'd8btrf1chrlqid',
        'USER': 'mblgmlnxabnoip',
        'PASSWORD': 'fd334241f5f4a93b8fd0de6f3a81ac87e42aef0979da7a4672d78e46eba7a02d',
        'HOST': 'ec2-107-20-155-148.compute-1.amazonaws.com',
        'PORT': '5432'
    }
}
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pluto',
        'USER': 'pluto',
        'PASSWORD': 'K65&&hyrt#@!hgrtr',
        'HOST': '127.0.0.1',   # Or an IP Address that your DB is hosted on
        'PORT': '',
        'OPTIONS': {
            'sql_mode': 'STRICT_TRANS_TABLES',
        }
    }
}


# SENDGRID
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = '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'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
