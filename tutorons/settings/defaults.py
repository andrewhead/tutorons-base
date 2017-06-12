#! /usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
import os
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DEPS_DIR = os.path.join(BASE_DIR, 'deps')

# Security
SECRET_KEY_FILE = os.path.join(
    os.path.expanduser('~'),
    '.tutorons', 'secret.key'
)
try:
    SECRET_KEY = open(SECRET_KEY_FILE).read()
except Exception as e:
    SECRET_KEY = "placeholder"
    logging.critical(
        "\nException when loading secret key (" + str(e) + ")\n" +
        "Using placeholder secret key.\nMake sure that a secret " +
        "key file is created at the location of SECRET_KEY_FILE " + 
        "(currently " + SECRET_KEY_FILE + ") by running:\n\n" + 
        "DJANGO_SETTINGS_MODULE=tutorons.settings.dev python " +
        "manage.py createsecretkey\n\n" + 
        "If that's what you're doing right now, then kudos!\n")
CORS_ORIGIN_ALLOW_ALL = True  # We're okay accepting connections from anywhere

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'tutorons.home',  # Home page
    'tutorons.core',  # Tools for parsing and explaining web pages
    # Add your Tutorons module here:
    'tutorons.modules.python_builtins',
)

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tutorons.middleware.crossdomain-middleware.XsSharing',
)

ROOT_URLCONF = 'tutorons.urls'

WSGI_APPLICATION = 'tutorons.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = []


# Load templates for each app
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
    },
]
