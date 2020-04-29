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
    'django.contrib.humanize',
    'apps.person.apps.PersonConfig',
    'apps.tryout.apps.TryoutConfig',
    'apps.market.apps.MarketConfig',
    'apps.payment.apps.PaymentConfig',
    'apps.mypoints.apps.MyPointsConfig',
    'apps.cms.apps.CmsConfig',
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
SESSION_LOGIN = True
CRISPY_TEMPLATE_PACK = 'bootstrap4'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
COIN_EXCHANGE = 1
SITE_NAME = 'Try Out'
COMMISSION = 2 # in percent
PAGINATION_PER_PAGE = 25


# Email Configuration
# https://docs.djangoproject.com/en/3.0/topics/email/
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# SendGrid
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = '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'
EMAIL_PORT = 587
EMAIL_USE_TLS = True


# Messages
# https://docs.djangoproject.com/en/3.0/ref/contrib/messages/
MESSAGE_TAGS = {
    messages.DEBUG: 'alert alert-dark',
    messages.INFO: 'alert alert-info',
    messages.SUCCESS: 'alert alert-info success',
    messages.WARNING: 'alert alert-warning',
    messages.ERROR: 'alert alert-error',
}


# Django Debug Toolbar
# https://django-debug-toolbar.readthedocs.io/en/stable/installation.html
if DEBUG:
    DEBUG_TOOLBAR_PATCH_SETTINGS = False
    INTERNAL_IPS = ('127.0.0.1', 'localhost',)
    MIDDLEWARE += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

    INSTALLED_APPS += (
        'debug_toolbar',
    )

    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ]

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }
