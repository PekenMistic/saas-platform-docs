from .base import *  # noqa: F401, F403

DEBUG = False

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

CORS_ALLOWED_ORIGIN_REGEXES = [
    r'^https://.*\.saas\.id$',
]

CACHES['default']['TIMEOUT'] = 3600  # noqa: F405

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'WARNING'},
        'apps': {'handlers': ['console'], 'level': 'WARNING'},
    },
}
