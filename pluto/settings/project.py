from django.contrib.messages import constants as messages

from .base import *

# Midtrans
from utils import midtransclient
snap = midtransclient.Snap()
snap.api_config.is_production=False
snap.api_config.server_key='SB-Mid-server-mQLSmNGfGW4frw2-kQ1icidB'
snap.api_config.client='SB-Mid-client-W08K_oXWFKYZc8QD'
SNAP = snap

# INSTALL APPLICATIONS
PROJECT_APPS = [
    'corsheaders',
    'rest_framework',
    'crispy_forms',
    'mathfilters',
    'django_celery_results',
    'django.contrib.humanize',
    'apps.person.apps.PersonConfig',
    'apps.tryout.apps.TryoutConfig',
    'apps.market.apps.MarketConfig',
    'apps.payment.apps.PaymentConfig',
    'apps.mypoints.apps.MyPointsConfig',
    'apps.cms.apps.CmsConfig',
    'gdstorage',
]

INSTALLED_APPS = INSTALLED_APPS + PROJECT_APPS


# Specifying authentication backends
# https://docs.djangoproject.com/en/3.0/topics/auth/customizing/
AUTHENTICATION_BACKENDS = ['apps.person.utils.auth.LoginBackend',]


# Application middleware
PROJECT_MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]
MIDDLEWARE = MIDDLEWARE + PROJECT_MIDDLEWARE


# Django Rest Framework (DRF)
# https://www.django-rest-framework.org/
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication'
    ],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.'
                                'NamespaceVersioning',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.'
                                'PageNumberPagination',
    'PAGE_SIZE': 2
}


# Project Configuration
PROJECT_NAME = 'Marketion'
PROJECT_WEBSITE = 'www.marketion.com'
SESSION_LOGIN = True
CRISPY_TEMPLATE_PACK = 'bootstrap4'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
COIN_EXCHANGE = 1
SITE_NAME = 'Try Out'
COMMISSION = 2 # in percent
PAGINATION_PER_PAGE = 25


# Google Drive
GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE = os.path.join(PROJECT_PATH, 'ornate-variety-276505-40aebde52af4.json')


# CACHING
# https://docs.djangoproject.com/en/2.2/topics/cache/
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "pluto_cache"
    }
}


# Messages
# https://docs.djangoproject.com/en/3.0/ref/contrib/messages/
MESSAGE_TAGS = {
    messages.DEBUG: 'alert alert-dark',
    messages.INFO: 'alert alert-info',
    messages.SUCCESS: 'alert alert-info success',
    messages.WARNING: 'alert alert-warning',
    messages.ERROR: 'alert alert-error',
}


# REDIS
REDIS_HOST = '127.0.0.1'
REDIS_PORT = '6379'
REDIS_URL = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
