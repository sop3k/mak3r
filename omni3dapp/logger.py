from logging import getLogger
from logging.config import dictConfig


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'formatters': {
        'console': {
            'format': '[%(asctime)s][%(levelname)s] %(name)s %(filename)s:%(funcName)s:%(lineno)d | %(message)s',
            'datefmt': '%H:%M:%S',
            },
        },

    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console'
            },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': 'http://2cfff87653054585be86df9f0fafc68e:5b73836a4be54f148bfc7cbd5dec35eb@sentry.studioply.com/5',
            },
        },

    'loggers': {
        '': {
            'handlers': ['console', 'sentry'],
            'level': 'DEBUG',
            'propagate': False,
            },
        'omniapp': {
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


dictConfig(LOGGING)
log = getLogger(__name__)
