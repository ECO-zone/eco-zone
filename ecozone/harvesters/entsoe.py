from datetime import UTC, datetime, timedelta
import logging
import os
from time import sleep
from typing import List, Tuple

from requests import Session

from ecozone.models import AggregateGenerationForecast, ControlArea, ForecastType, PSRGeneration, PsrType, RenewableGenerationForecast, Generation, PSR_TYPES_POST_2024, Forecast
from ecozone.utils import round_date_to_quarter_hour


logger = logging.getLogger(__name__)


ENTSOE_SECURITY_TOKEN = os.getenv("ENTSOE_SECURITY_TOKEN")
if not ENTSOE_SECURITY_TOKEN:
    raise Exception("ENTSOE_SECURITY_TOKEN is required.")


API_URL = "https://web-api.tp.entsoe.eu/api"


DEFAULT_START_DATE = datetime(year=2022, month=12, day=31, hour=23, tzinfo=UTC)


# def get_last_start_date(control_area: ControlArea, psr: PsrType) -> datetime:
#     last_record = (
#         PSRGeneration.objects.filter(control_area=control_area.value, psr=psr)
#         .order_by("start")
#         .last()
#     )
#     if last_record:
#         return last_record.start
#     else:
#         return DEFAULT_START_DATE
def get_last_start_date(psr: PsrType) -> datetime:
    last_record = (
        Generation.objects.filter(**{f"{psr}_gen__isnull": False})
        .order_by("start")
        .last()
    )
    if last_record:
        return last_record.start
    else:
        return DEFAULT_START_DATE

def harvest_psr_generation(historical: bool = False, **kwargs):
    for control_area in [ControlArea.GERMANY]:
        for psr_type in [PsrType.B16, PsrType.B18, PsrType.B19]: # PSR_TYPES_POST_2024:
            logger.info(
                f"Harvesting psr generation for {psr_type.label} in {control_area.label}..."
            )
            periods: List[Tuple[datetime, datetime]] = []
            if historical:
                initial_start_date = DEFAULT_START_DATE
                final_start_date = get_last_start_date(psr_type)
                if initial_start_date == final_start_date:
                    final_start_date = round_date_to_quarter_hour(datetime.now(UTC))
                end_date = initial_start_date + timedelta(days=366)
                periods.append((initial_start_date, end_date))
                while end_date <= final_start_date:
                    start_date = end_date + timedelta(minutes=15)
                    end_date = start_date + timedelta(days=366)
                    periods.append((start_date, end_date))
            else:
                last_start_date = (
                    DEFAULT_START_DATE
                    if historical
                    else get_last_start_date(psr_type)
                )
                logger.info(
                    f"Last record for {psr_type.label} in {control_area.label} is from {last_start_date}"
                )
                start_date = last_start_date - timedelta(days=7)
                max_date = start_date + timedelta(days=366)
                end_date = round_date_to_quarter_hour(datetime.now(UTC))
                if max_date < end_date:
                    end_date = max_date
                periods.append((start_date, end_date))
            for start_date, end_date in periods:
                # Format datetimes according to ENTSO-E's strange requirements.
                # Set minutes to 0 because the ENTSO-E API requires a minutes value
                # but only accepts `00`.
                start = start_date.strftime("%Y%m%d%H%M")
                end = end_date.strftime("%Y%m%d%H%M")
                params = {
                    "periodStart": start,
                    "periodEnd": end,
                    "securityToken": ENTSOE_SECURITY_TOKEN,
                    "documentType": "A75",
                    "processType": "A16",
                    "in_Domain": control_area.value,
                    "psrType": psr_type.value.upper(),
                }
                session = Session()
                try:
                    r = session.get(API_URL, params=params, timeout=100)
                    r.raise_for_status()
                except Exception:
                    logger.exception("Harvester error: unable to get ENTSO-E data.")
                    continue
                Generation.objects.import_records(
                    r.content,
                )
        logger.info(f"Finished harvesting records in {control_area}")
    logger.info("Finished harvesting ENTSO-E generation records.")
    logger.info("Updating timeseries generation fields.")


def harvest_renewable_generation_forecast(forecast_type: ForecastType):
    forecast_type: str
    match forecast_type:
        case ForecastType.DAYAHEAD:
            forecast_type = "A01"
        case ForecastType.INTRADAY:
            forecast_type = "A40"
        case ForecastType.CURRENT:
            forecast_type = "A18"
    for control_area in [ControlArea.GERMANY]:
        for psr_type in [PsrType.B16, PsrType.B18, PsrType.B19]:
            logger.info(
                f"Harvesting psr generation for {psr_type.label} in {control_area.label}..."
            )
            start_date = round_date_to_quarter_hour(datetime.now(UTC))
            logger.info(
                f"Last record for {psr_type.label} in {control_area.label} is from {start_date}"
            )
            end_date = round_date_to_quarter_hour(datetime.now(UTC)) + timedelta(days=2)
            # Format datetimes according to ENTSO-E's strange requirements.
            start = start_date.strftime("%Y%m%d%H%M")
            end = end_date.strftime("%Y%m%d%H%M")
            params = {
                "periodStart": start,
                "periodEnd": end,
                "securityToken": ENTSOE_SECURITY_TOKEN,
                "documentType": "A69",
                "processType": forecast_type,
                "in_Domain": control_area.value,
                "psrType": psr_type.value.upper(),
            }
            session = Session()
            try:
                r = session.get(API_URL, params=params, timeout=100)
                r.raise_for_status()
            except Exception:
                logger.warning("Harvester error: unable to get ENTSO-E data.")
                continue
            Forecast.objects.import_records(
                r.content, forecast_type
            )
            sleep(2)
        logger.info(f"Finished harvesting records in {control_area}")
    logger.info("Finished harvesting ENTSO-E generation records.")
    logger.info("Updating timeseries generation fields.")


def harvest_aggregate_generation_forecast():
    for control_area in [ControlArea.GERMANY]:
        logger.info(
            f"Harvesting aggregate generation forecast for {control_area.label}..."
        )
        start_date = round_date_to_quarter_hour(datetime.now(UTC))
        logger.info(
            f"Last record for {control_area.label} is from {start_date}"
        )
        end_date = start_date + timedelta(days=2)
        # Format datetimes according to ENTSO-E's strange requirements.
        # Set minutes to 0 because the ENTSO-E API requires a minutes value
        # but only accepts `00`.
        start = start_date.strftime("%Y%m%d%H00")
        end = end_date.strftime("%Y%m%d%H00")
        params = {
            "periodStart": start,
            "periodEnd": end,
            "securityToken": ENTSOE_SECURITY_TOKEN,
            "documentType": "A71",
            "processType": "A01",
            "in_Domain": control_area.value,
        }
        session = Session()
        try:
            r = session.get(API_URL, params=params, timeout=100)
            r.raise_for_status()
        except Exception:
            logger.exception("Harvester error: unable to get ENTSO-E data.")
            continue
        Forecast.objects.import_aggregate_records(
            r.content,
        )
        sleep(2)
        logger.info(f"Finished harvesting records in {control_area}")
    logger.info("Finished harvesting ENTSO-E generation records.")
    logger.info("Updating timeseries generation fields.")
