from django.conf import settings


def git_rev(request):
    return {"git_rev": settings.GIT_REV}
