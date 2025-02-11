from pathlib import Path
import os
import dj_database_url
from decouple import config, Csv
from requests import Session
from requests_ntlm import HttpNtlmAuth
from zeep import Client
from requests.auth import HTTPBasicAuth
from zeep.transports import Transport


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


MODE = config("MODE", default="dev")
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "vmdf",
    }
}

ALLOWED_HOSTS = [".localhost", ".127.0.0.1"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "authentication",
    "base",
    "dashboard",
    "registration",
    "pharmaceutical",
    "vaccine",
    "pesticide",
    "feed",
    "biocidal",
    "devices",
    "variation",
    "appeal",
    "payment",
    "retention",
    "renewal",
    "gmp",
    "myRequest",
    "permit",
    "retailers",
    "advertisement",
    "disposal",
    "manufacturing",
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
if config("MODE") == "prod":
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    CONTENT_SECURITY_POLICY = "default-src 'self'; script-src 'self'; style-src 'self';"

ROOT_URLCONF = "VMD.urls"

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

WSGI_APPLICATION = "VMD.wsgi.application"


# Send Email Settings

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "vmdkenya@gmail.com"
EMAIL_HOST_PASSWORD = "nzaczcevzyscxvez"
EMAIL_USE_TLS = True
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = "vmdkenya@gmail.com"

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

ENCRYPT_KEY = b"bzKNyzSwwsN0pwQKglGqPnMKPS6WTPElkRPoCOTYN0I="


STATIC_URL = "/static/"
MEDIA_URL = "/images/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# configuring the location for media
MEDIA_URL = "/images/"
MEDIA_ROOT = os.path.join(BASE_DIR, "images")


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


AUTHS = Session()

WEB_SERVICE_PWD = "Password@312"
WEB_SERVICE_UID = "KTL-ADMIN"

BASE_URL = "http://20.120.96.92:2047/BC200/WS/VMD%20TEST%20LIVE/Codeunit/WebPortal"
O_DATA = "http://20.120.96.92:2048/BC200/ODataV4/Company(%27VMD%20TEST%20LIVE%27){}"
AUTHS.auth = HTTPBasicAuth("KTL-ADMIN", WEB_SERVICE_PWD)

CLIENT = Client(BASE_URL, transport=Transport(session=AUTHS))
AUTHS = HTTPBasicAuth("KTL-ADMIN", WEB_SERVICE_PWD)
