"""
Production-ready logging configuration for Django.
Simple, clean, and follows best practices.
"""

import sys
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR.parent / 'logs'

# Ensure logs directory exists
LOGS_DIR.mkdir(exist_ok=True)


def get_logging_config(environment='production'):
    """
    Get logging configuration based on environment.

    Args:
        environment: 'development', 'staging', or 'production'

    Returns:
        Dict with Django LOGGING configuration
    """

    is_development = environment == 'development'

    # Check if running tests
    is_testing = 'test' in sys.argv or 'pytest' in sys.modules

    # If running tests, return minimal/disabled logging config
    if is_testing:
        return {
            'version': 1,
            'disable_existing_loggers': True,
            'handlers': {
                'null': {
                    'class': 'logging.NullHandler',
                },
            },
            'root': {
                'handlers': ['null'],
            },
            'loggers': {
                '': {
                    'handlers': ['null'],
                    'level': 'CRITICAL',
                    'propagate': False,
                },
                'django': {
                    'handlers': ['null'],
                    'level': 'CRITICAL',
                    'propagate': False,
                },
                'django.request': {
                    'handlers': ['null'],
                    'level': 'CRITICAL',
                    'propagate': False,
                },
                'django.security': {
                    'handlers': ['null'],
                    'level': 'CRITICAL',
                    'propagate': False,
                },
                'django.db.backends': {
                    'handlers': ['null'],
                    'level': 'CRITICAL',
                    'propagate': False,
                },
                'apps': {
                    'handlers': ['null'],
                    'level': 'CRITICAL',
                    'propagate': False,
                },
            },
        }

    config = {
        'version': 1,
        'disable_existing_loggers': False,

        # ==========================================
        # Formatters
        # ==========================================
        'formatters': {
            'verbose': {
                'format': '[{levelname}] {asctime} | {name} | {module}.{funcName}:{lineno} | {message}',
                'style': '{',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'simple': {
                'format': '[{levelname}] {asctime} | {message}',
                'style': '{',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },

        # ==========================================
        # Filters
        # ==========================================
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse',
            },
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },

        # ==========================================
        # Handlers
        # ==========================================
        'handlers': {
            # Console output
            'console': {
                'level': 'DEBUG' if is_development else 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },

            # Main application log
            'file_app': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': LOGS_DIR / 'app.log',
                'maxBytes': 10 * 1024 * 1024,  # 10 MB
                'backupCount': 10,
                'formatter': 'verbose',
                'encoding': 'utf-8',
            },

            # Error log (WARNING and above)
            'file_error': {
                'level': 'WARNING',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': LOGS_DIR / 'error.log',
                'maxBytes': 10 * 1024 * 1024,  # 10 MB
                'backupCount': 10,
                'formatter': 'verbose',
                'encoding': 'utf-8',
            },

            # Security log
            'file_security': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': LOGS_DIR / 'security.log',
                'maxBytes': 10 * 1024 * 1024,  # 10 MB
                'backupCount': 10,
                'formatter': 'verbose',
                'encoding': 'utf-8',
            },

            # Database queries (development only)
            'file_db': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': LOGS_DIR / 'db.log',
                'maxBytes': 10 * 1024 * 1024,  # 10 MB
                'backupCount': 5,
                'formatter': 'simple',
                'encoding': 'utf-8',
                'filters': ['require_debug_true'],
            },

            # Email admins on errors (production only)
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler',
                'filters': ['require_debug_false'],
                'formatter': 'verbose',
            },
        },

        # ==========================================
        # Loggers
        # ==========================================
        'loggers': {
            # Root logger
            '': {
                'handlers': ['console', 'file_app', 'file_error'],
                'level': 'INFO',
                'propagate': False,
            },

            # Django framework
            'django': {
                'handlers': ['console', 'file_app', 'file_error'],
                'level': 'INFO',
                'propagate': False,
            },

            # Django request/response (captures 500 errors)
            'django.request': {
                'handlers': ['console', 'file_error', 'mail_admins'],
                'level': 'ERROR',
                'propagate': False,
            },

            # Django security
            'django.security': {
                'handlers': ['console', 'file_security'],
                'level': 'INFO',
                'propagate': False,
            },

            # Database queries
            'django.db.backends': {
                'handlers': ['file_db'] if is_development else [],
                'level': 'DEBUG' if is_development else 'INFO',
                'propagate': False,
            },

            # Your apps (automatically catches apps.*)
            'apps': {
                'handlers': ['console', 'file_app', 'file_error'],
                'level': 'DEBUG' if is_development else 'INFO',
                'propagate': False,
            },
        },
    }

    return config