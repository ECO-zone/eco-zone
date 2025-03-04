from datetime import datetime
from typing import List, Optional, Tuple

from ninja import NinjaAPI, Schema

from .models import (
    EmissionFactorsNordSued,
    Generation,
    RegionNorthSouth,
    TimeseriesRedispatch,
)


api = NinjaAPI(
    title="ECO zone API",
    version="1",
    description="Dies ist die interaktive Dokumentation für die ECO Zone API. ECO Zone ist ein Open-Source-Projekt. Den vollständigen Quellcode finden Sie unter https://github.com/ECO-zone/eco-zone.",
)


class RedispatchData(Schema):
    header: Tuple[str, str, str] = (
        "start",
        "power_mid_mw_decrease",
        "power_mid_mw_increase",
    )
    rows: List[Tuple[datetime, float, float]] = (
        (datetime.fromisoformat("2025-01-01T00:00:00Z"), 4634.030000000001, 3981.6),
    )


@api.get("/timeseries/redispatch", response=RedispatchData)
def get_timeseries_redispatch(
    request, start: Optional[datetime] = None, end: Optional[datetime] = None
):
    result = TimeseriesRedispatch.objects.get_timeseries_data(start, end)

    return RedispatchData(header=result[0], rows=result[1:])


class ClassifiedRedispatchData(Schema):
    header: Tuple[str, str, str, str, str] = (
        "start",
        "res_reduce_power_south",
        "res_reduce_power_north",
        "con_increase_power_south",
        "con_increase_power_north",
    )
    rows: List[Tuple[datetime, float, float, float, float]] = (
        (
            datetime.fromisoformat("2025-01-01T00:00:00Z"),
            0,
            200.86,
            1426.9299999999998,
            0,
        ),
    )


@api.get("/timeseries/classified_redispatch", response=ClassifiedRedispatchData)
def get_timeseries_classified_redispatch(
    request, start: Optional[datetime] = None, end: Optional[datetime] = None
):
    result = TimeseriesRedispatch.objects.get_timeseries_classified_redispatch_data(
        start, end
    )

    return ClassifiedRedispatchData(header=result[0], rows=result[1:])


class NationalEmissionIntensityData(Schema):
    header: Tuple[str, str] = ("start", "emission_intensity")
    rows: List[Tuple[datetime, float]] = (
        (datetime.fromisoformat("2025-01-14T00:00:00Z"), 390.24490576535226),
    )


@api.get("/timeseries/emission-intensity", response=NationalEmissionIntensityData)
def get_emission_intensity(
    request, start: Optional[datetime] = None, end: Optional[datetime] = None
):
    result = Generation.objects.get_emission_intensity_data(start, end)

    return NationalEmissionIntensityData(header=result[0], rows=result[1:])


class ZonalEmissionIntensityData(Schema):
    header: Tuple[str, str, str] = (
        "start",
        "emission_intensity_north",
        "emission_intensity",
    )
    rows: List[Tuple[datetime, float, float]] = (
        (datetime.fromisoformat("2025-01-14T00:00:00Z"), 390.24490576535226, 150.0),
    )


@api.get("/timeseries/emission-intensity-zonal", response=ZonalEmissionIntensityData)
def get_emission_intensity_for_region(
    request,
    region: RegionNorthSouth,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
):
    result = Generation.objects.get_emission_intensity_data_for_region(
        region, start, end
    )

    return ZonalEmissionIntensityData(header=result[0], rows=result[1:])


class GenerationData(Schema):
    header: Tuple[
        str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str
    ] = (
        "start",
        "B01",
        "B02",
        "B04",
        "B05",
        "B06",
        "B09",
        "B10",
        "B11",
        "B12",
        "B15",
        "B16",
        "B17",
        "B18",
        "B19",
        "B20",
    )
    rows: List[
        Tuple[
            datetime,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
        ]
    ] = (
        (
            datetime.fromisoformat("2025-01-14T00:00:00Z"),
            4350,
            9701,
            10685,
            5735,
            378,
            27,
            138,
            1420,
            153,
            79,
            0,
            671,
            6298,
            17635,
            246,
        ),
    )


@api.get("/timeseries/generation", response=GenerationData)
def get_generation(
    request, start: Optional[datetime] = None, end: Optional[datetime] = None
):
    result = Generation.objects.get_generation_data(start, end)

    return GenerationData(header=result[0], rows=result[1:])


class EmissionData(Schema):
    header: Tuple[
        str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str
    ] = (
        "start",
        "B01",
        "B02",
        "B04",
        "B05",
        "B06",
        "B09",
        "B10",
        "B11",
        "B12",
        "B15",
        "B16",
        "B17",
        "B18",
        "B19",
        "B20",
    )
    rows: List[
        Tuple[
            datetime,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
        ]
    ] = (
        (
            datetime.fromisoformat("2025-01-14T00:00:00Z"),
            133762.5,
            2607143.75,
            1121925,
            1337688.75,
            103761,
            33.75,
            172.5,
            1065,
            114.75,
            98.75,
            0,
            184189.5,
            14170.5,
            39678.75,
            67527,
        ),
    )


@api.get("/timeseries/emissions", response=EmissionData)
def get_emissions(
    request, start: Optional[datetime] = None, end: Optional[datetime] = None
):
    result = Generation.objects.get_emissions_data(start, end)

    return EmissionData(header=result[0], rows=result[1:])


@api.get("/stats/emission-factors", response=EmissionFactorsNordSued)
def get_emission_factors(request):
    return Generation.objects.get_emission_factors_nord_sued()
