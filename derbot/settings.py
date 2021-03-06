"""
Django settings for derbot project.

Generated by 'django-admin startproject' using Django 3.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path

import environ
from redis import ConnectionPool
from mastodon import Mastodon
import requests

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

# reading .env file
environ.Env.read_env(env_file=str(BASE_DIR.joinpath(".env")))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY", default="")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "huey.contrib.djhuey",
    "import_export",
    "derbot.names.apps.NamesConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "derbot.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "derbot.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": env.db("DB_URL", default="sqlite:///db.sqlite3")
    # {
    #     # 'ENGINE': 'django.db.backends.sqlite3',
    #     # 'NAME': BASE_DIR / 'db.sqlite3',
    # }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = env("LANGUAGE_CODE", default="en-us")

TIME_ZONE = env("TIME_ZONE", default="US/Central")

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

# STATICFILES_DIRS = [
#     BASE_DIR.joinpath('static'),
# ]

STATIC_ROOT = BASE_DIR.joinpath("static")
STATIC_URL = "/static/"


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REDIS_URL = env("REDIS_URL", default="")

HUEY = {
    "immediate": env.bool("TASKS_IMMEDIATE", default=False),
    "results": True,  # Store return values of tasks.
    "store_none": False,  # If a task returns None, do not save to results.
    "utc": True,
    "consumer": {
        "workers": env.int("WORKERS", default=3),
        "worker_type": "thread",
        "initial_delay": 0.1,  # Smallest polling interval, same as -d.
        "backoff": 1.15,  # Exponential backoff using this rate, -b.
        "max_delay": 10.0,  # Max possible polling interval, -m.
        "scheduler_interval": 1,  # Check schedule every second, -s.
        "periodic": True,  # Enable crontab feature.
        "check_worker_health": True,  # Enable worker health checks.
        "health_check_interval": 1,  # Check worker health every second.
    },
}

if REDIS_URL:
    HUEY["huey_class"] = "huey.PriorityRedisHuey"
    pool = ConnectionPool().from_url(REDIS_URL)
    HUEY["connection"] = {"connection_pool": pool}
else:
    HUEY["huey_class"] = "huey.SqliteHuey"
    HUEY["filename"] = "tasks.sqlite3"

API_BASE_URL = env("API_BASE_URL", default="https://botsin.space")
ACCESS_TOKEN = env("ACCESS_TOKEN", default=None)
MASTO = Mastodon(
    access_token=ACCESS_TOKEN, api_base_url=API_BASE_URL, ratelimit_method="pace"
)

ACTUALLY_TOOT = env("ACTUALLY_TOOT", default=True, cast=bool)

MODEL_NAME = env("MODEL_NAME", default="derbynames")
NAME_BUFFER_SIZE = env("NAME_BUFFER_SIZE", default=100)

DEFAULT_TEMP = env("DEFAULT_TEMP", default=1.0)
USE_RANDOM_TEMPS = env("USE_RANDOM_TEMPS", default=True, cast=bool)
MIN_TEMP = env("MIN_TEMP", default=0.2, cast=float)
MAX_TEMP = env("MAX_TEMP", default=1.0, cast=float)

DO_WAIT = env("DO_WAIT", default=True, cast=bool)
MIN_WAIT = env("MIN_WAIT", default=10, cast=int)
MAX_WAIT = env("MAX_WAIT", default=300, cast=int)

DATA_UPLOAD_MAX_NUMBER_FIELDS = env("DATA_UPLOAD_MAX_NUMBER_FIELDS", default=None)

SESSION = requests.session()
REQUEST_TIMEOUT = env("REQUEST_TIMEOUT", default=15)

COLOR_BOT = env('COLOR_BOT', default='accessibleColors@botsin.space')