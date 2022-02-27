"""
Django settings for dz project.
"""
import os
from pathlib import Path
from environs import Env
import dj_database_url

env = Env()
env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env.str('SECRET_KEY')

DEBUG = env.bool('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')


# Application definition
	@@ -72,7 +69,10 @@

WSGI_APPLICATION = 'dz.wsgi.application'

DATABASES = {"default": env.dj_db_url("DB_URL")}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators
	@@ -127,19 +127,12 @@

LOGIN_URL = '/profiles/login/'

BASE_URL = env.str('BASE_URL')

if not DEBUG:
    EMAIL_HOST = env.str('EMAIL_HOST')
    EMAIL_PORT = env.str('EMAIL_PORT')
    EMAIL_HOST_USER = env.str('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD')
    EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS')
    EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL')
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = '25'
    EMAIL_HOST_USER = 'test@test.test'
    EMAIL_HOST_PASSWORD = 'test'
<<<<<<< HEAD
    EMAIL_USE_SSL = False
=======
    EMAIL_USE_SSL = False
>>>>>>> origin/visits2
