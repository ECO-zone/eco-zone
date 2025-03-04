from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt


def index(request, *args, **kwargs):
    return render(request, "index.html", {})


def usecases(request, *args, **kwargs):
    return render(request, "usecases.html", {})


def methodology(request, *args, **kwargs):
    return render(request, "methodology.html", {})


# Iframes #
###########


@xframe_options_exempt
def emissions_intensity_zonal(request, *args, **kwargs):
    return render(
        request,
        "chart.html",
        {
            "title": "Emissionsintensität zonal",
            "chart_id": "timeseries-emission-intensity-zonal",
        },
    )


@xframe_options_exempt
def redispatch(request, *args, **kwargs):
    return render(
        request,
        "chart.html",
        {"title": "Redispatch-Leistung", "chart_id": "timeseries-redispatch"},
    )


@xframe_options_exempt
def classified_redispatch(request, *args, **kwargs):
    return render(
        request,
        "chart.html",
        {
            "title": "Geordnete Redispatch-Leistung",
            "chart_id": "timeseries-classified-redispatch",
        },
    )


@xframe_options_exempt
def emissions_intensity_germany(request, *args, **kwargs):
    return render(
        request,
        "chart.html",
        {
            "title": "Emissionsintensität Deutschland",
            "chart_id": "timeseries-emission-intensity",
        },
    )


@xframe_options_exempt
def generation(request, *args, **kwargs):
    return render(
        request,
        "chart.html",
        {
            "title": "Nettostromerzeugung pro Energieträger",
            "chart_id": "timeseries-generation",
        },
    )


@xframe_options_exempt
def emissions(request, *args, **kwargs):
    return render(
        request,
        "chart.html",
        {"title": "Emissionsintensität zonal", "chart_id": "timeseries-emissions"},
    )


@xframe_options_exempt
def zone_map(request, *args, **kwargs):
    return render(request, "map.html", {})
