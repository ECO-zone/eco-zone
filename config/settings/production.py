import os
import re

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *
from .base import GIT_REV, SENTRY_DSN_BACKEND, SENTRY_ENVIRONMENT


sentry_sdk.init(
    dsn=SENTRY_DSN_BACKEND,
    environment=SENTRY_ENVIRONMENT,
    integrations=[DjangoIntegration()],
    release=GIT_REV,
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
    traces_sample_rate=0,  # Don't send any transactions to Sentry while we're on the free plan
)


DEBUG = False

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    USER, PASSWORD, HOST, PORT, NAME = re.match(  # type: ignore
        "^postgres://(?P<username>.*?)\:(?P<password>.*?)\@(?P<host>.*?)\:(?P<port>\d+)\/(?P<db>.*?)$",  # noqa: W605
        DATABASE_URL,
    ).groups()
else:
    USER = PASSWORD = HOST = NAME = "postgres"
    PORT = 5432

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": NAME,
        "USER": USER,
        "PASSWORD": PASSWORD,
        "HOST": HOST,
        "PORT": int(PORT),
    }
}

STATIC_ROOT = BASE_DIR / "staticfiles"
