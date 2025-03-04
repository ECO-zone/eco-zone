import os


os.environ["NINJA_SKIP_REGISTRY"] = (
    "yes"  # https://github.com/vitalik/django-ninja/issues/229
)
