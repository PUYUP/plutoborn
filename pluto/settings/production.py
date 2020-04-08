from .base import *
from .project import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', 'pluto-tryout.herokuapp.com']


# Django Sessions
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/2.2/ref/settings/
# SESSION_COOKIE_SECURE = True
# SESSION_COOKIE_SAMESITE = None
# SESSION_COOKIE_HTTPONLY = True

# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_SSL_REDIRECT = True
# X_FRAME_OPTIONS = 'DENY'


# Django csrf
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/2.2/ref/csrf/
# CSRF_COOKIE_SECURE = True
# CSRF_TRUSTED_ORIGINS = [
#     'opsional001.firebaseapp.com'
# ]


# Django CORS
# ------------------------------------------------------------------------------
# https://pypi.org/project/django-cors-headers/
# CORS_ALLOW_CREDENTIALS = True
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

# Add configuration for static files storage using whitenoise
# STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
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
