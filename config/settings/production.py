import os
import re

import sentry_sdk

from .base import *


sentry_sdk.init(
    dsn="https://3f5894b6ebf51aa161706c7b546e5327@o467902.ingest.us.sentry.io/4507407118893056",
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
