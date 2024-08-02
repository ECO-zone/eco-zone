from datetime import datetime
from typing import List, Optional, Union

from ninja import NinjaAPI

from .models import PSRGeneration, RegionDena, RegionNorthSouth, TimeseriesRedispatch


api = NinjaAPI(title="ECO zone API")


@api.get("/timeseries/redispatch", response=List[list])
def get_timeseries_redispatch(
    request, start: Optional[datetime] = None, end: Optional[datetime] = None
):
    return TimeseriesRedispatch.objects.get_timeseries_data(start, end)


@api.get("/timeseries/emission-intensity", response=List[list])
def get_emission_intensity(
    request, start: Optional[datetime] = None, end: Optional[datetime] = None
):
    return PSRGeneration.objects.get_emission_intensity_data(start, end)

@api.get("/timeseries/emission-intensity-zonal", response=List[list])
def get_emission_intensity_for_region(
    request, region: str, start: Optional[datetime] = None, end: Optional[datetime] = None
):
    print(region)
    print(start)
    return PSRGeneration.objects.get_emission_intensity_data_for_region(region, start, end)


@api.get("/timeseries/generation", response=List[list])
def get_generation(
    request, start: Optional[datetime] = None, end: Optional[datetime] = None
):
    return PSRGeneration.objects.get_generation_data(start, end)


@api.get("/timeseries/emissions", response=List[list])
def get_generation(
    request, start: Optional[datetime] = None, end: Optional[datetime] = None
):
    return PSRGeneration.objects.get_emissions_data(start, end)
