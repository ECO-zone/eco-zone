from csv import DictReader
from datetime import datetime, timedelta, UTC
from io import StringIO
import logging
import os
from time import sleep
from uuid import uuid4

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from django.db import transaction
from django.db.models import Q

from ..models import GridRegion, PowerPlant, Redispatch, TimeseriesRedispatch, TSO


logger = logging.getLogger(__name__)


def get_env_var(value: str) -> str:
    env_var = os.getenv(value)
    if not value:
        raise Exception(f"{value} is not set.")

    return env_var


def get_timespan(start: datetime, end: datetime) -> str:
    _format = "%Y-%m-%dT%H:%M"

    return f"{start.strftime(_format)}/{end.strftime(_format)}"


def from_de_format_to_float(value: str) -> float:
    return float(value.replace(",", "."))


def from_date_and_time_to_utc_datetime(date: str, time: str) -> datetime:
    return datetime.strptime(f"{date}{time}Z", "%d.%m.%Y%H:%M%z")


def harvest_redispatch() -> int:
    CLIENT_ID = get_env_var("NETZTRANZPARENZ_CLIENT_ID")
    CLIENT_SECRET = get_env_var("NETZTRANZPARENZ_CLIENT_SECRET")
    TOKEN_URL = "https://identity.netztransparenz.de/users/connect/token"
    current_grid_regions = GridRegion.objects.get_dict_of_names_to_ids()
    current_power_plants = PowerPlant.objects.get_dict_of_names_to_ids()
    current_tsos = TSO.objects.get_dict_of_names_to_ids()
    client = OAuth2Session(client=BackendApplicationClient(CLIENT_ID))
    client.fetch_token(
        token_url=TOKEN_URL, client_id=CLIENT_SECRET, client_secret=CLIENT_SECRET
    )
    last_record = Redispatch.objects.order_by("start").last()
    if last_record:
        start = last_record.start
    else:
        start = datetime(year=2023, month=1, day=1, tzinfo=UTC)
    end = start + timedelta(days=30)
    now = datetime.now(UTC)
    if end > now:
        end = now
    timespan = get_timespan(start, end)
    records_to_check = Redispatch.objects.filter(
        Q(start__gte=start - timedelta(days=7)) & Q(start__lte=end + timedelta(days=7))
    ).all()
    record_check_set = {x.make_record_comparison_str() for x in records_to_check}
    r = client.get(f"https://ds.netztransparenz.de/api/v1/data/redispatch/{timespan}")
    reader = DictReader(StringIO(r.text), delimiter=";")
    redispatches = []
    redispatch_region_relations = []
    for row in reader:
        record = {}
        record_id = uuid4()
        record["id"] = record_id
        record["pk"] = record_id
        record["start"] = from_date_and_time_to_utc_datetime(
            row["BEGINN_DATUM"], row["BEGINN_UHRZEIT"]
        )
        record["end"] = from_date_and_time_to_utc_datetime(
            row["ENDE_DATUM"], row["ENDE_UHRZEIT"]
        )
        region_names = [s.strip() for s in row["NETZREGION"].split(",")]
        for region_name in region_names:
            region_id = current_grid_regions.get(region_name)
            if not region_id:
                new_region = GridRegion.objects.create(name=region_name)
                current_grid_regions[new_region.name] = new_region.id
                region_id = new_region.id
            redispatch_region_relations.append(
                Redispatch.grid_regions.through(
                    redispatch_id=record_id, gridregion_id=region_id
                )
            )
        record["reason"] = row["GRUND_DER_MASSNAHME"]
        record["direction"] = row["RICHTUNG"]
        record["power_mid_mw"] = from_de_format_to_float(row["MITTLERE_LEISTUNG_MW"])
        record["power_max_mw"] = from_de_format_to_float(row["MAXIMALE_LEISTUNG_MW"])
        record["work_total_mwh"] = from_de_format_to_float(row["GESAMTE_ARBEIT_MWH"])
        tso_s_name = row["ANWEISENDER_UENB"]
        tso_s = current_tsos.get(tso_s_name)
        if not tso_s:
            new_tso_s = TSO.objects.create(name=tso_s_name)
            current_tsos[new_tso_s.name] = new_tso_s.id
            tso_s = new_tso_s.id
        record["tso_supplying_id"] = tso_s
        tso_r_name = row["ANFORDERNDER_UENB"]
        tso_r = current_tsos.get(tso_r_name)
        if not tso_r:
            new_tso_r = TSO.objects.create(name=tso_r_name)
            current_tsos[new_tso_r.name] = new_tso_r.id
            tso_r = new_tso_r.id
        record["tso_requesting_id"] = tso_r
        power_plant_name = row["BETROFFENE_ANLAGE"]
        power_plant = current_power_plants.get(power_plant_name)
        if not power_plant:
            new_power_plant = PowerPlant.objects.create(name=power_plant_name)
            current_power_plants[new_power_plant.name] = new_power_plant.id
            power_plant = new_power_plant.id
        record["power_plant_id"] = power_plant
        redispatch = Redispatch(**record)
        # Skip any records that already exist
        record_comparison_str = redispatch.make_record_comparison_str()
        if record_comparison_str not in record_check_set:
            redispatches.append(redispatch)
            # There are duplicate entries in the Netztranzparenz data, so we need to filter them too.
            record_check_set.add(record_comparison_str)
    with transaction.atomic():
        new_redispatch_records = Redispatch.objects.bulk_create(
            redispatches, batch_size=1000
        )
        new_redispatch_records_set = {x.id for x in new_redispatch_records}
        redispatch_region_relations_to_create = [
            x
            for x in redispatch_region_relations
            if x.redispatch_id in new_redispatch_records_set
        ]
        Redispatch.grid_regions.through.objects.bulk_create(
            redispatch_region_relations_to_create, batch_size=1000
        )
        TimeseriesRedispatch.objects.update_from_redispatch_records(
            new_redispatch_records
        )

    return len(new_redispatch_records_set)


def harvest_redispatch_to_present() -> int:
    total = 0

    while True:
        results = harvest_redispatch()
        total += results
        if not results:
            break
        sleep(1)  # Avoid making requests too quickly to prevent being blocked.

    return results
