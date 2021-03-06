"""
Django settings for valuarte project.

Generated by 'django-admin startproject' using Django 1.10.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'w2^+4=c)d0+$*al=$**0^_2+l)6_@(_!m$a9ozfv2h(!mi^*6x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'dbbackup',
    'dtracking',
    'facturacion',
    'background_task',
    'base',
    'geoposition',
    'grappelli_dynamic_navbar',
    'import_export',
    'grappelli',
    'adminactions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'home',
    'djangobower',
    'crispy_forms',
    'colorfield',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'valuarte.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'valuarte.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'valuarte',
        'USER': 'postgres',
        'PASSWORD': 'ABC123#$',
        'HOST': 'localhost',
        # 'HOST': 'www.valuarte.com.ni',
        'PORT': '5432',
    },
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'es-NI'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

GEOPOSITION_GOOGLE_MAPS_API_KEY = 'AIzaSyBjWBugqqWF-lwi6opFnCrDtg6SVj6hlME'

# Variables para el envio por gmail


#EMAIL_USE_TLS = True
EMAIL_USE_SSL = True
EMAIL_HOST = 'ts000433.ferozo.com'
EMAIL_HOST_USER = 'sistema@valuarte.com.ni'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = 'SVal2017'
EMAIL_PORT = 465

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',

)

BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR, 'components/')

BOWER_PATH = '/usr/local/bin/bower'

BOWER_INSTALLED_APPS = [
     'Ionicons#2.0.1',
     'bootstrap#4.0.0-beta',
     'd3#3.1.1',
     'font-awesome#4.7.0',
     'fullcalendar#3.5.1',
     'izimodal#1.5.1',
     'jquery#2.2.4',
     'jquery-datetime-picker-bygiro#5ee6dfc88f9a4bdb7cc17513b4e78db415c3c658',
     'jquery-ui#1.12.1',
     'leaflet#1.2.0',
     'moment#2.18.1',
     'pnotify#3.2.1',
     'popper.js#1.12.5'
]



WKHTMLTOPDF_CMD_OPTIONS = {
    'quiet': True,
}

CRISPY_TEMPLATE_PACK = "bootstrap3"

# reporte diario
EMAILS_REPORTE_DIARIO ="sistema@valuarte.com.ni,mario.rojas@valuarte@valuarte.com.ni,gerardo.calderon@valuarte.com.ni,paola.ubeda@valuarte.com.ni,elvis.rivera@segdel.com,gerencia@segdel.com,mario.rojas@valuarte.com.ni,gerencia@valuarte.com.ni"
EMAILS_FACTURACION = "mario.rojas@valuarte.com.ni,gerencia@valuarte.com.ni"
#DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
#DBBACKUP_STORAGE_OPTIONS = {'location': '/var/backups/valuarte'}

"""DBBACKUP_STORAGE = 'storages.backends.ftp.FTPStorage'
DBBACKUP_STORAGE_OPTIONS = {
    'location': 'ftp://ftp_@geosaldana.com:Delta2017@ftp.geosaldana.com:21'
}"""
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': '/var/backups/valuarte'}

DBBACKUP_CONNECTORS = {
'default': {
'USER': 'postgres',
'PASSWORD': 'ABC123#$',
'HOST': 'localhost'
}
}
GRAPPELLI_SWITCH_USER = "True"
