from logging import getLogger
from logging.config import dictConfig
from raven.handlers.logging import SentryHandler


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'formatters': {
        'file': {
            'format': '[%(asctime)s][%(levelname)s] %(name)s %(filename)s:%(funcName)s:%(lineno)d | %(message)s',
            'datefmt': '%H:%M:%S',
            },
        },

    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'file',
            'filename': 'mak3r.log',
            'maxBytes': 1048576,
            'backupCount': 3,
            },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': 'http://2cfff87653054585be86df9f0fafc68e:5b73836a4be54f148bfc7cbd5dec35eb@sentry.studioply.com/5',
            },
        },

    'loggers': {
        '': {
            'handlers': ['file', 'sentry'],
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
