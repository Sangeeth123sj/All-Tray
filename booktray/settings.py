"""
Django settings for booktray project.

Generated by 'django-admin startproject' using Django 3.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
from pathlib import Path


import django
from django.utils.encoding import force_str
django.utils.encoding.force_text = force_str
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "-lo^_fjlxwcn*!d03^fy!-tb%c)4_-wfrp9mf8=p70yb#h$mup"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# authentication backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "booktray.backend.MyBackend",
]
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "tray.backend.MyBackend",
]

# Application definition

# email configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = "sangeeth123sj@gmail.com"
EMAIL_HOST_PASSWORD = "yfvsdnjrnetdklld"

LOGIN_URL = "entry"

INSTALLED_APPS = [
    "users",
    "tray.apps.TrayConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "crispy_forms",
    "django_extensions",
    # "graphene_django",
    "payments",
    'import_export',
    'django_crontab',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "booktray.urls"

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
                "django.template.context_processors.media",
            ],
        },
    },
]

WSGI_APPLICATION = "booktray.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = "users.User"


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"
TIME_INPUT_FORMATS = [
    "%I:%M %p",  # 6:22 PM
    "%I %p",  # 6 PM
    "%I:%M:%S %p",  # 6:22:44 PM
    "%H:%M:%S",  # '14:30:59'
    "%H:%M:%S.%f",  # '14:30:59.000200'
    "%H:%M",  # '14:30'
]

USE_I18N = True

USE_L10N = True

USE_TZ = True

CRISPY_TEMPLATE_PACK = "bootstrap4"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"

STATICFILES_DIRS = (os.path.join(BASE_DIR, "/var/www/static/"),)

STATIC_ROOT = "var/www/static/"


SESSION_SAVE_EVERY_REQUEST = True


# Activate Django-Heroku.
# django_heroku.settings(locals())


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}


def get_cache():
    import os

    try:
        servers = os.environ["MEMCACHIER_SERVERS"]
        username = os.environ["MEMCACHIER_USERNAME"]
        password = os.environ["MEMCACHIER_PASSWORD"]
        return {
            "default": {
                "BACKEND": "django.core.cache.backends.memcached.PyLibMCCache",
                # TIMEOUT is not the connection timeout! It's the default expiration
                # timeout that should be applied to keys! Setting it to `None`
                # disables expiration.
                "TIMEOUT": None,
                "LOCATION": servers,
                "OPTIONS": {
                    "binary": True,
                    "username": username,
                    "password": password,
                    "behaviors": {
                        # Enable faster IO
                        "no_block": True,
                        "tcp_nodelay": True,
                        # Keep connection alive
                        "tcp_keepalive": True,
                        # Timeout settings
                        "connect_timeout": 2000,  # ms
                        "send_timeout": 750 * 1000,  # us
                        "receive_timeout": 750 * 1000,  # us
                        "_poll_timeout": 2000,  # ms
                        # Better failover
                        "ketama": True,
                        "remove_failed": 1,
                        "retry_timeout": 2,
                        "dead_timeout": 30,
                    },
                },
            }
        }
    except:
        return {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


CACHES = get_cache()

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"


GRAPH_MODELS = {
    "all_applications": True,
    "group_models": True,
}

GRAPHENE = {"SCHEMA": "booktray.schema.schema"}

PAYTM_MERCHANT_ID = 'AillzC86868525023191'

PAYTM_SECRET_KEY = 'GDMJNBUUMh&#zn9K'

PAYTM_WEBSITE = 'DEFAULT'

PAYTM_CHANNEL_ID = 'WEB'

PAYTM_INDUSTRY_TYPE_ID = 'Retail'

RAZORPAY_MERCHANT_ID = "KXsjdQfz8cyAFM"

RAZORPAY_KEY_SECRET = "LLLbj9bvyg6M0aHpOK4bphC1"

RAZORPAY_KEY_ID = "rzp_test_sv9b6ulPTe1ydd"

RAZORPAY_SUBSCRIPTION_ID = 'sub_KY0nie3ffRqcPu'

SUBSCRIPTION_CALLBACK_URL = "http://127.0.0.1:8000/college_subscription_callback"
# "https://sangeethjoseph.pythonanywhere.com/college_subscription_callback"

RECHARGE_CALLBACK_URL = "http://127.0.0.1:8000/callback"
# "https://sangeethjoseph.pythonanywhere.com/callback"

BASIC_PLAN_ID = "plan_KY0lxlEjAXMJwR"



CRONJOBS = [
    ('*/5 * * * *', 'tray.management.commands.subscription_revenue_update')
]
