"""
Django settings for eVoting_Ceni project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
from django.contrib import messages
from celery.schedules import crontab
import sentry_sdk # type: ignore

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-4l^0fsh63cl=%49^x)^byz0zlhre$ipi_0xp4rkt_p)=y6h@re'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'tz_detect',
    'axes',
    'django_celery_beat',
    'users',
    'administration',
    'elector',
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_session_timeout.middleware.SessionTimeoutMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
    'tz_detect.middleware.TimezoneMiddleware',
]

ROOT_URLCONF = 'eVoting_Ceni.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'eVoting_Ceni.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3', 
    }
}

""" DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'evoting_ceni_db',
        'USER': 'elkis_dev',
        'PASSWORD': 'elkis_dev_00,
        'HOST': 'db',
        'PORT': '5432',
        'OPTIONS': {
            'client_encoding': 'UTF8',
        },
    }
}
"""
# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Les configurations de django_axes

# nombre maximal de tentatives échouées
AXES_FAILURE_LIMIT = 5

# Durée de verrouillage
AXES_COOLOFF_TIME = 1

# Controle de verrouillage
AXES_LOCK_OUT_AT_FAILURE = False

# Activation ou desactivation de django_axes
AXES_ENABLED = True

# Security configurations

# Active le filtre XSS intégré du navigateur pour protéger contre les attaques XSS.
SECURE_BROWSER_XSS_FILTER = True

# Empêche les navigateurs de deviner le type MIME du contenu pour éviter les attaques de type MIME sniffing.
SECURE_CONTENT_TYPE_NOSNIFF = True

# Empêche l'affichage de la page dans un cadre (iframe) pour protéger contre le Clickjacking.
X_FRAME_OPTIONS = 'DENY'

# Rend le cookie de session inaccessible via JavaScript pour protéger contre le vol de session via XSS.
SESSION_COOKIE_HTTPONLY = True

# Expire la session de l'utilisateur à la fermeture du navigateur pour renforcer la sécurité.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# La session de l'utilisateur expire après 30 minutes d'inactivité
SESSION_EXPIRE_SECONDS = 1800

# La session est prolongée à chaque activité
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True

# Rediriger l'utilisateur après expiration
SESSION_TIMEOUT_REDIRECT = 'logout'

# Les configurations cryptographiques

# Sel utilisé pour ajouter une sécurité supplémentaire lors du hachage des données sensibles.
HASH_SALT = '25Jr3SSk_PiYg2_CV3bQJUgm'

# Clé secrète utilisée pour le chiffrement des données sensibles.
ENCRYPTION_KEY = 'f2a1c3d4e5b6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2'

# Vecteur d'initialisation (IV) utilisé pour ajouter une randomisation au chiffrement, assurant que les mêmes données chiffrées avec la même clé produisent un texte chiffré différent à chaque fois.
ENCRYPTION_IV = '3f5a7c9e1b2d4f6a8c0e2f1a3d4c5b6a'

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'fr'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

TZ_DETECT_IP_ENABLED = True

TZ_DETECT_BROWSER_ENABLED = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]


MEDIA_ROOT = os.path.join(BASE_DIR, 'media') 

MEDIA_URL = '/media/'

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

# Celery configuration

# Url de configuration vers le broker rabbitmq
BROKER_URL = 'pyamqp://guest:guest@localhost:5672//'

""" Adresse du broker utilisé par Celery pour envoyer et recevoir des tâches.
Ici, 'localhost' signifie que le broker est hébergé localement sur la même machine que l'application. """
CELERY_BROKER_HOST = 'localhost'

CELERY_RESULT_BACKEND = 'rpc://'

""" Indique que Celery doit automatiquement réessayer de se connecter au broker lors du démarrage
si la connexion échoue initialement. Cela permet d'éviter les interruptions dues à des problèmes
temporaires de connexion avec le broker de messages. """
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True


""" Configuration de l'ordonnancement périodique de Celery Beat.
Cette tâche exécute la fonction `backup_database` définie dans `users.tasks` toutes les 30 minutes.
'backup-every' est le nom de la tâche programmée, et la planification est définie par `crontab(minute='*/30')`
qui spécifie que la tâche doit être exécutée à chaque demi-heure. """
CELERY_BEAT_SCHEDULE = {
    'backup-every': {
        'task': 'users.tasks.backup_database',
        'schedule': crontab(minute='*/1'),
    },
}

# Utilise le planificateur de tâches basé sur la base de données de Django Celery Beat
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Django-secured-fields configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'edev5513@gmail.com'
EMAIL_HOST_PASSWORD = 'gqcovwddwuglhjxr'

LOGIN_URL = '/signin/'

# configuration du fichier log
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '{asctime} {levelname} [{module}.{funcName}:{lineno}] {message}',
            'style': '{',
        },
        'verbose': {
            'format': '{asctime} {levelname} {module} {message} [File: {pathname}, Line: {lineno}]',
            'style': '{',
        },
    },
    'handlers': {
        'django_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django.log'),
            'formatter': 'standard',
        },
        'my_logger_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'my_logger.log'),
            'formatter': 'verbose',
        },
        'db_backend_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'db_backends.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['django_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'my_logger': {
            'handlers': ['my_logger_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['db_backend_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

sentry_sdk.init(
    dsn="https://89dc2b29a518cc255dacaace836ceaa6@o4507830838165504.ingest.us.sentry.io/4507881855188992",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)