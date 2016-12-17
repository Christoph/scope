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

CURRENT_NAME = 'scope'
CURRENT_SLOGAN = "see more"

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'explore',
    'scope',
    'alert',
    'captcha',
    'curate',
    'twitter_bootstrap',
    'django.contrib.sites',
    'widget_tweaks',
    'djangobower')


ADMINS = ('GRPHT', 'grphtcontact@gmail.com', 'admin@scope.ai', 'robot@scope.ai')

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

EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend'
EMAIL_HOST = 'smtp.zoho.com'
EMAIL_PORT = 465
EMAIL_USE_TSL = False
EMAIL_USE_SSL = True
SERVER_EMAIL = im.get_env_variable('OUT_EMAIL')
EMAIL_HOST_USER = im.get_env_variable('OUT_EMAIL')
DEFAULT_FROM_EMAIL = im.get_env_variable('OUT_EMAIL')
EMAIL_HOST_PASSWORD = im.get_env_variable('EMAIL_HOST_PASSWORD')
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
                    'conf.context_processors.check_login',
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

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "data")

]

BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR, '../components/')

BOWER_INSTALLED_APPS = (
    "jquery-ui",
    "bootstrap",
    "bootstrap-select",
    "d3#3",
    "lodash",
    "font-awesome",
)

STATIC_ROOT = os.path.join(BASE_DIR, '../static/')
STATIC_URL = '/static/'
LOGIN_REDIRECT_URL = '/profile'
