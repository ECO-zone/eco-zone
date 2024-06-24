import json

from django.conf import settings


def git_rev(request):
    return {"git_rev": settings.GIT_REV}


def sentry_cdn_url(request):
    return {"sentry_cdn_url": json.dumps(settings.SENTRY_CDN_URL)}


def sentry_env(request):
    return {"sentry_env": json.dumps(settings.SENTRY_ENVIRONMENT)}


def sentry_release(request):
    return {"sentry_release": json.dumps(settings.GIT_REV)}
