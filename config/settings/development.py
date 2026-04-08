from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# Debug toolbar temporarily disabled due to network issues
# INSTALLED_APPS += [
#     'debug_toolbar',
# ]

# MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

INTERNAL_IPS = [
    '127.0.0.1',
]

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Debug toolbar config
# DEBUG_TOOLBAR_CONFIG = {
#     'SHOW_TOOLBAR_CALLBACK': lambda request: True,
# }

LOGGING['loggers']['django']['level'] = 'DEBUG'
