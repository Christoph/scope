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

from conf.settings.importer import ImportGlobal
from conf.settings.base import *

im = ImportGlobal()

DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1']
CURRENT_DOMAIN = 'http://127.0.0.1:8000'

SITE_ID = 1

DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql_psycopg2',
                         'NAME': im.get_env_variable('DATABASE_NAME'),
                         'USER': im.get_env_variable('DATABASE_USER'),
                         'PASSWORD': im.get_env_variable('DATABASE_PASSWORD'),
                         'HOST': 'localhost',
                         'PORT': ''}}


STATICFILES_DIRS += [
    os.path.join(BASE_DIR, "static"),
]

# STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
