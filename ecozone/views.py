from datetime import datetime, UTC
from django.shortcuts import render

from ecozone.models import Redispatch


def index(request, *args, **kwargs):
    regions_dena = Redispatch.objects.get_valid_regions_dena(start=datetime(2024, 1, 1, tzinfo=UTC), end=None)
 
    return render(request, "index.html", {"regions_dena": regions_dena})
