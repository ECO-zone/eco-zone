from datetime import datetime, UTC
from django.shortcuts import render

from ecozone.models import Redispatch


def index(request, *args, **kwargs):
    regions_dena = Redispatch.objects.get_valid_regions_dena(start=datetime(2024, 1, 1, tzinfo=UTC), end=None)
 
    return render(request, "index.html", {"regions_dena": regions_dena})

def emissions_intensity_zonal(request, *args, **kwargs):
    regions_dena = Redispatch.objects.get_valid_regions_dena(start=datetime(2024, 1, 1, tzinfo=UTC), end=None)

    return render(request, "chart.html", {"title": "Emissionsintensität zonal", "regions_dena": regions_dena, "chart_id": "timeseries-emission-intensity-zonal"})


def redispatch(request, *args, **kwargs):
    return render(request, "chart.html", {"title": "Redispatch-Leistung", "chart_id": "timeseries-redispatch"})


def emissions_intensity_germany(request, *args, **kwargs):
    return render(request, "chart.html", {"title": "Emissionsintensität Deutschland", "chart_id": "timeseries-emission-intensity"})


def generation(request, *args, **kwargs):
    return render(request, "chart.html", {"title": "Nettostromerzeugung pro Energieträger", "chart_id": "timeseries-generation"})


def emissions(request, *args, **kwargs):
    return render(request, "chart.html", {"title": "Emissionsintensität zonal", "chart_id": "timeseries-emissions"})


def zone_map(request, *args, **kwargs):
    return render(request, "map.html", {})


def usecases(request, *args, **kwargs): 
    return render(request, "usecases.html", {})


def methodology(request, *args, **kwargs): 
    return render(request, "methodology.html", {})


def recommendations(request, *args, **kwargs): 
    return render(request, "recommendations.html", {})
