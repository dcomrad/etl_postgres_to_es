from django.conf import settings

if settings.DEBUG:
    settings.INSTALLED_APPS.append('debug_toolbar')

if settings.DEBUG:
    settings.MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

INTERNAL_IPS = ['127.0.0.1']
