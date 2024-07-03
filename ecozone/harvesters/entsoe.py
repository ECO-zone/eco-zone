from datetime import UTC, datetime, timedelta
import logging
import os

from requests import Session

from ..models import ControlArea, PSRGeneration, PsrType


logger = logging.getLogger(__name__)


ENTSOE_SECURITY_TOKEN = os.getenv("ENTSOE_SECURITY_TOKEN")
if not ENTSOE_SECURITY_TOKEN:
    raise Exception("ENTSOE_SECURITY_TOKEN is required.")


API_URL = "https://web-api.tp.entsoe.eu/api"


def get_last_start_date(control_area: ControlArea, psr: PsrType) -> datetime:
    last_record = (
        PSRGeneration.objects.filter(control_area=control_area.value, psr=psr)
        .order_by("start")
        .last()
    )
    if last_record:
        return last_record.start
    else:
        return datetime(year=2023, month=12, day=31, hour=23, tzinfo=UTC)


def round_date_to_quarter_hour(date):
    hour_ratio = date.minute / 60
    if hour_ratio < 0.25:
        minutes = 0
    elif hour_ratio < 0.5:
        minutes = 15
    elif hour_ratio < 0.75:
        minutes = 30
    else:
        minutes = 45

    return date + timedelta(minutes=minutes - date.minute)


def harvest_psr_generation(**kwargs):
    for control_area in ControlArea:
        for psr_type in PsrType:
            logger.info(
                f"Harvesting psr generation for {psr_type.label} in {control_area.label}..."
            )
            last_start_date = get_last_start_date(control_area, psr_type)
            logger.info(
                f"Last record for {psr_type.label} in {control_area.label} is from {last_start_date}"
            )
            start_date = last_start_date - timedelta(days=7)
            max_date = start_date + timedelta(days=366)
            end_date = round_date_to_quarter_hour(datetime.now(UTC))
            if max_date < end_date:
                end_date = max_date
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
                logger.warning("Harvester error: unable to get ENTSO-E data.")
                return
            PSRGeneration.objects.import_records(
                r.content,
            )
        logger.info(f"Finished harvesting records in {control_area}")
    logger.info("Finished harvesting ENTSO-E generation records.")
    logger.info("Updating timeseries generation fields.")
