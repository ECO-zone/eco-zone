from datetime import datetime
from typing import List, Optional

from ninja import NinjaAPI

from .models import EmissionFactorsNordSued, Generation, RegionNorthSouth, TimeseriesRedispatch


api = NinjaAPI(
    title="ECO zone API",
    version="1",
    description="Dies ist die interaktive Dokumentation für die ECO Zone API. ECO Zone ist ein Open-Source-Projekt. Den vollständigen Quellcode finden Sie unter https://github.com/ECO-zone/eco-zone."
)


@api.get("/timeseries/redispatch", response=List[list])
def get_timeseries_redispatch(
    request, start: Optional[datetime] = None, end: Optional[datetime] = None
):
    return TimeseriesRedispatch.objects.get_timeseries_data(start, end)


@api.get("/timeseries/emission-intensity", response=List[list])
def get_emission_intensity(
    request, start: Optional[datetime] = None, end: Optional[datetime] = None
):
    print("api called")
    return Generation.objects.get_emission_intensity_data(start, end)

@api.get("/timeseries/emission-intensity-zonal", response=List[list])
def get_emission_intensity_for_region(
    request, region: RegionNorthSouth, start: Optional[datetime] = None, end: Optional[datetime] = None
):
    return Generation.objects.get_emission_intensity_data_for_region(region, start, end)


@api.get("/timeseries/generation", response=List[list])
def get_generation(
    request, start: Optional[datetime] = None, end: Optional[datetime] = None
):
    return Generation.objects.get_generation_data(start, end)


@api.get("/timeseries/emissions", response=List[list])
def get_emissions(
    request, start: Optional[datetime] = None, end: Optional[datetime] = None
):
    return Generation.objects.get_emissions_data(start, end)


@api.get("/stats/emission-factors", response=EmissionFactorsNordSued)
def get_emission_factors(request):
    return Generation.objects.get_emission_factors_nord_sued()