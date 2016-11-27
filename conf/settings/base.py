# -*- coding: utf-8 -*-

""" Local settings.

Django settings for graphite project.
bladibli
Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/

"""

from .importer import ImportGlobal
import os

im = ImportGlobal()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SECRET_KEY = im.get_env_variable('SECRET_KEY')
X_FRAME_OPTIONS = 'DENY'

ADMINS = ('GRPHT', 'grphtcontact@gmail.com', 'admin@scope.ai')

SITE_ID = 1

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware')

GOOGLE_ANALYTICS = {'google_analytics_id': 'UA-71839611-1'}
ROOT_URLCONF = 'conf.urls'
EMAIL_HOST = 'smtp.zoho.com'
EMAIL_PORT = '465'
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'robot@scope.ai'
EMAIL_HOST_PASSWORD = 'scope2016'
AUTH_PROFILE_MODULE = 'scope.UserProfile'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates',
              'DIRS': [os.path.join(BASE_DIR, 'templates')],
              'APP_DIRS': True,
              'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'conf.context_processors.site',
                    'django.contrib.messages.context_processors.messages']}}]

WSGI_APPLICATION = 'conf.wsgi.application'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',
)

BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR, '../components/')

BOWER_INSTALLED_APPS = (
    "jquery-ui",
    "bootstrap",
    "bootstrap-select",
    "d3",
    "lodash",
    "font-awesome",
)

STATIC_ROOT = 'static/'
MEDIA_ROOT = 'media/'
TEMPLATE_ROOT = 'templates/'

STATIC_URL = '/static/'

STATIC_BREV = 'last24h'