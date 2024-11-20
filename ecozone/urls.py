from django.urls import path

from . import views
from .api import api


urlpatterns = [
    path("", views.index, name="index"),
    path("api/", api.urls),
]

charts = ["emissions_intensity_zonal", "redispatch", "emissions_intensity_germany", "generation", "emissions"]
chart_urls = [path(f"charts/{chart}", getattr(views, chart), name=chart) for chart in charts]

urlpatterns.extend(chart_urls)

urlpatterns.append(path("maps/zone_map", views.zone_map, name="zone_map"))
