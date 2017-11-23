import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, '../static'))
IMPORT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '../import'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ""

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

ADMINS = [('John', 'john@example.com'), ('Mary', 'mary@example.com')]

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'gateway_db',
        'USER': 'gateway_user',
        'PASSWORD': 'supersecure',
        'HOST': '192.168.49.49',
        'PORT': '5432',
    }
}

CELERY_BROKER_URL = 'amqp://admin:admin@192.168.49.50:5672/processing'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379'


EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/poster-app'

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 25
# EMAIL_HOST_USER = ''
# EMAIL_HOST_PASSWORD = ''
# EMAIL_USE_TLS = False
# DEFAULT_FROM_EMAIL = 'Trained monkey <monkey@example.com>'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/opt/poster-app/logs/django.log',
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
        },
        'request_handler': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/opt/poster-app/logs/django_request.log',
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

#######################################################################################################################
# ---------------------------------- SETTINGS FOR processing/pmo ---------------------------------------------------- #
#######################################################################################################################
# https://docs.python.org/3/library/ftplib.html
# class ftplib.FTP(host='', user='', passwd='', acct='', timeout=None, source_address=None)
PMO_FTP = {
    'host': '',
    'user': '',
    'passwd': '',
}
