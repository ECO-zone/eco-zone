import csv
from datetime import UTC, datetime, timedelta
import logging
from typing import Optional, Union
from pathlib import Path
from uuid import uuid4
from xml.etree import ElementTree

from django.db import models, transaction
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce


logger = logging.getLogger(__name__)


class RegionNorthSouth(models.TextChoices):
    NORTH = "north", "Nord"
    SOUTH = "south", "Süd"


class GridRegionManager(models.Manager):

    def get_dict_of_names_to_ids(self):
        return {x["name"]: x["id"] for x in self.values("name", "id").all()}


class GridRegion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = GridRegionManager()

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                name="unique_grid_region_record",
            )
        ]


class TSOManager(models.Manager):

    def get_dict_of_names_to_ids(self):
        return {x["name"]: x["id"] for x in self.values("name", "id").all()}


class TSO(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = TSOManager()

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                name="unique_tso_record",
            )
        ]


def is_float(value):
    try:
        float(value)
        return True
    except Exception:
        return False


class PowerPlantManager(models.Manager):

    def get_dict_of_names_to_ids(self):
        return {x["name"]: x["id"] for x in self.values("name", "id").all()}

    def update_zone_data(self) -> int:
        with open(Path(__file__).parent.parent / "data" / "zones_2024_08_05.csv", "r") as f:
            reader = csv.DictReader(f)
            plants_from_file = []
            for row in reader:
                name = row["Name"]
                _region_north_south = row["Nord-Süd"]
                region_north_south: Optional[RegionNorthSouth]
                if not _region_north_south:
                    region_north_south = None
                else:
                    try:
                        if _region_north_south == "Nord":
                            _region_north_south = "north"
                        elif _region_north_south == "Süd":
                            _region_north_south = "south"
                        region_north_south = RegionNorthSouth(_region_north_south)
                    except Exception:
                        logger.info(f"{name} has invalid north/south region '{_region_north_south}'")
                        region_north_south = None
                        pass
                _region_dena = row["Dena Regionen"]
                region_dena = Optional[str]
                if not _region_dena:
                    region_dena = None
                else:
                    if len(_region_dena) == 2 and is_float(_region_dena[0]) and is_float(_region_dena[1]):
                        region_dena = _region_dena
                    else:
                        logger.info(f"{name} has invalid dena region '{_region_dena}'")
                        region_dena = None
                _is_renewable=row["EE/nicht EE"]
                is_renewable: Optional[bool]
                if not _is_renewable:
                    is_renewable = None
                else:
                    if _is_renewable not in {"EE", "nicht EE"}:
                        logger.info(f"{name} has invalid renewable status '{_is_renewable}'")
                        pass
                    else:
                        if _is_renewable == "EE":
                            is_renewable = True
                        else:
                            is_renewable = False
                plants_from_file.append(
                    PowerPlant(
                        name=name,
                        region_dena=region_dena,
                        region_north_south=region_north_south,
                        is_renewable=is_renewable,
                    )
                )
            current_plants = {x.name: x for x in self.all()}
            plants_to_update = []
            attrs = ["region_dena", "region_north_south", "is_renewable"]
            for plant_from_file in plants_from_file:
                update = False
                current_plant = current_plants.get(plant_from_file.name)
                if not current_plant:
                    logger.info(f"Could not find plant '{plants_from_file.name}'")
                else:
                    for attr in attrs:
                        new_value = getattr(plant_from_file, attr)
                        if getattr(current_plant, attr) != new_value:
                            update = True
                            setattr(current_plant, attr, new_value)
                if update:
                    plants_to_update.append(current_plant)
            if plants_to_update:
                self.bulk_update(plants_to_update, attrs)
            
            return len(plants_to_update)

    def get_regions_dena(self):
        return PowerPlant.objects.filter(region_dena__isnull=False).values("region_dena").distinct().order_by("region_dena").values_list("region_dena", flat=True)


class PowerPlant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100)
    region_dena = models.CharField(
        verbose_name="Region (dena)",
        max_length=2,
        null=True
    )
    region_north_south = models.CharField(
        verbose_name="Region (Nord/Süd)",
        max_length=5,
        choices=RegionNorthSouth.choices,
        null=True
    )
    is_renewable = models.BooleanField(
        verbose_name="EE Anlage",
        null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = PowerPlantManager()

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                name="unique_power_plant_record",
            )
        ]


RegionDena = str


class RedispatchManager(models.Manager):

    def get_valid_regions_dena(self, start: Optional[datetime], end: Optional[datetime]):
        timerange_query = Q()
        if start:
            timerange_query &= Q(start__gte=start)
        if end:
            timerange_query &= Q(start__lt=end)
        records = (
            self.filter(timerange_query)
            .filter(direction="Wirkleistungseinspeisung reduzieren")
            .filter(power_plant__region_dena__isnull=False)
            .filter(power_plant__is_renewable=True)
            .values("power_plant__region_dena")
            .distinct()
            .order_by("power_plant__region_dena")
            .values_list("power_plant__region_dena", flat=True)
        )

        return records

    def get_timeranges(self, region: Union[RegionDena, RegionNorthSouth], start: Optional[datetime], end: Optional[datetime]):
        timerange_query = Q()
        if start:
            timerange_query &= Q(start__gte=start)
        if end:
            timerange_query &= Q(start__lt=end)
        if region in RegionNorthSouth:
            region_lookup = "region_north_south"
        elif isinstance(region, RegionDena):
            region_lookup = "region_dena"
        records = (
            self.filter(timerange_query)
            .filter(direction="Wirkleistungseinspeisung reduzieren")
            .filter(**{f"power_plant__{region_lookup}": region})
            .filter(power_plant__is_renewable=True)
            .values("start")
            .order_by("start")
            .values_list("start", "end")
        )
        timeranges = []
        for r in records:
            if not timeranges:
                timeranges.append([r[0], r[1]])
            else:
                last = timeranges[-1]
                rend = r[1]
                rstart = r[0]
                # If the end of the new timerange is less than or equal
                # to the end of the last time range, then it falls within
                # the last timerange. If it is greater than the last end,
                # then we either need to extend the last timerange by replacing
                # the end or create a new time range. We extend the last
                # timerange if the the start is less than or equal to the last
                # end and we create a new timerange if the start is greater
                # than the last end.
                if rend > last[1]:
                    if rstart <= last[0]:
                        last[1] = rend
                    else:
                        timeranges.append([rstart, rend])
        return timeranges

class Redispatch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    start = models.DateTimeField(null=False)
    end = models.DateTimeField(null=False)
    grid_regions = models.ManyToManyField(GridRegion)
    reason = models.CharField(max_length=100, null=False)
    direction = models.CharField(max_length=100, null=False)
    power_mid_mw = models.FloatField(null=False)
    power_max_mw = models.FloatField(null=False)
    work_total_mwh = models.FloatField(null=False)
    tso_supplying = models.ForeignKey(
        TSO, on_delete=models.CASCADE, related_name="redispatch_tso_supplying"
    )
    tso_requesting = models.ForeignKey(
        TSO, on_delete=models.CASCADE, related_name="redispatch_tso_requesting"
    )
    power_plant = models.ForeignKey(PowerPlant, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = RedispatchManager()

    class Meta:
        indexes = [
            models.Index(fields=["start", "end", "power_plant"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "start",
                    "end",
                    "reason",
                    "direction",
                    "power_mid_mw",
                    "power_max_mw",
                    "work_total_mwh",
                    "tso_supplying",
                    "tso_requesting",
                    "power_plant",
                ],
                name="unique_redispatch_record",
            )
        ]

    def make_record_comparison_str(self) -> str:
        return f"{self.start.strftime("%Y-%m-%dT%H:%M")}-{self.end.strftime("%Y-%m-%dT%H:%M")}-{self.reason}-{self.direction}-{self.power_mid_mw}-{self.power_max_mw}-{self.work_total_mwh}-{self.tso_supplying_id}-{self.tso_requesting_id}-{self.power_plant_id}"


class TimeseriesRedispatchManager(models.Manager):

    def update_from_redispatch_records(self, redispatch_records):
        timeseries_records = []
        for redispatch_record in redispatch_records:
            start = redispatch_record.start
            end = redispatch_record.end
            while start < end:
                timeseries_records.append(
                    TimeseriesRedispatch(
                        start=start,
                        direction=redispatch_record.direction,
                        power_mid_mw=redispatch_record.power_mid_mw,
                        region_north_south=redispatch_record.power_plant.region_north_south,
                        is_renewable=redispatch_record.power_plant.is_renewable,
                        redispatch_id=redispatch_record.id,
                    )
                )
                start = start + timedelta(minutes=15)
        self.bulk_create(timeseries_records, batch_size=1000)

    def get_timeseries_data(self, start: Optional[datetime], end: Optional[datetime]):
        header = ["start", "power_mid_mw_decrease", "power_mid_mw_increase"]
        timerange_query = Q()
        if start:
            timerange_query &= Q(start__gte=start)
        if end:
            timerange_query &= Q(start__lt=end)
        records = (
            TimeseriesRedispatch.objects.filter(timerange_query)
            .values(
                "start",
            )
            .order_by("start")
            .annotate(
                power_mid_mw_decrease=Coalesce(
                    Sum(
                        "power_mid_mw",
                        filter=Q(direction="Wirkleistungseinspeisung reduzieren"),
                    ),
                    0.0,
                )
            )
            .annotate(
                power_mid_mw_increase=Coalesce(
                    Sum(
                        "power_mid_mw",
                        filter=Q(direction="Wirkleistungseinspeisung erhöhen"),
                    ),
                    0.0,
                )
            )
            .values_list(*header)
        )
        return [header] + list(records)
    
    def get_timeseries_renewable_status(self, region: RegionNorthSouth, start: Optional[datetime], end: Optional[datetime]):
        header = ["start", "renewable_factor"]
        timerange_query = Q()
        if start:
            timerange_query &= Q(start__gte=start)
        if end:
            timerange_query &= Q(start__lt=end)
        records = (
            TimeseriesRedispatch.objects.filter(timerange_query)
            .filter(region_north_south=region)
            .filter(is_renewable=True)
            .values(
                "start",
            )
            .order_by("start")
            .annotate(
                renewable_factor=Coalesce(
                    Sum(
                        "is_renewable",
                        filter=Q(direction="Wirkleistungseinspeisung reduzieren"),
                    ),
                    0.0,
                )
            )
            .values_list(*header)
        )
        return [header] + list(records)


class TimeseriesRedispatch(models.Model):
    start = models.DateTimeField(null=False)
    direction = models.CharField(max_length=100, null=False)
    power_mid_mw = models.FloatField(null=False)
    region_north_south = models.CharField(
        verbose_name="Region (Nord/Süd)",
        max_length=5,
        choices=RegionNorthSouth.choices,
        null=True
    )
    is_renewable = models.BooleanField(null=True)
    redispatch = models.ForeignKey(Redispatch, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = TimeseriesRedispatchManager()

    class Meta:
        indexes = [
            models.Index(fields=["start", "direction"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "start",
                    "redispatch",
                ],
                name="unique_timeseries_redispatch_record",
            )
        ]


class ControlArea(models.TextChoices):
    _50Hertz = "10YDE-VE-------2", "50Hertz"
    AMPRION = "10YDE-RWENET---I", "Amprion"
    TENNET = "10YDE-EON------1", "TenneT"
    TRANSNETBW = "10YDE-ENBW-----N", "TransnetBW"


class PsrType(models.TextChoices):
    B01 = "b01", "Biomasse"
    B02 = "b02", "Braunkohle"
    B03 = "b03", "Fossil Coal-derived gas"
    B04 = "b04", "Erdgas"
    B05 = "b05", "Steinkohle"
    B06 = "b06", "Mineralöl"
    B07 = "b07", "Fossil Oil shale"
    B08 = "b08", "Fossil Peat"
    B09 = "b09", "Geothermie"
    B10 = "b10", "Pumpspeicher"
    B11 = "b11", "Wasserkraft (Laufwasser)"
    B12 = "b12", "Wasserspeicher"
    B13 = "b13", "Marine"
    B14 = "b14", "Kernenergie"
    B15 = "b15", "Sonstige Erneuerbare Energien"
    B16 = "b16", "Photovoltaik"
    B17 = "b17", "Abfall"
    B18 = "b18", "Windenergie (Offshore-Anlage)"
    B19 = "b19", "Windenergie (Onshore-Anlage)"
    B20 = "b20", "Sonstige konventionelle Energien"


PSR_TYPES_POST_2024 = [
    x
    for x in PsrType
    if x not in {PsrType.B03, PsrType.B07, PsrType.B08, PsrType.B13, PsrType.B14}
]


class PSRGenerationManager(models.Manager):

    def import_records(self, xml):
        print("Starting import")
        name_spaces = {
            "entsoe": "urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0"
        }
        etree = ElementTree.fromstring(xml)
        points = []
        for entry in etree.findall("./entsoe:TimeSeries", name_spaces):
            try:
                control_area = ControlArea(
                    entry.find("./entsoe:inBiddingZone_Domain.mRID", name_spaces).text
                )
            except AttributeError:
                continue
            resolution = entry.find(
                "./entsoe:Period/entsoe:resolution", name_spaces
            ).text
            if resolution != "PT15M":
                continue
            psr = PsrType(
                entry.find(
                    "./entsoe:MktPSRType/entsoe:psrType", name_spaces
                ).text.lower()
            )
            start = datetime.fromisoformat(
                entry.find(
                    "./entsoe:Period/entsoe:timeInterval/entsoe:start", name_spaces
                ).text
            )
            for item in entry.findall(
                "./entsoe:Period/entsoe:Point/entsoe:quantity", name_spaces
            ):
                point = {"start": start, "value": int(item.text)}
                points.append(point)
                start += timedelta(minutes=15)
            query = (
                self.filter(
                    Q(start__gte=points[0]["start"]) & Q(start__lte=points[-1]["start"])
                )
                .filter(control_area=control_area)
                .filter(psr=psr)
            )
            records_to_check = {r.start: r for r in query.all()}
            records_to_create = []
            records_to_update = []
            updated_at = datetime.now(UTC)
            for point in points:
                old_record = records_to_check.get(point["start"])
                if old_record:
                    if old_record.power_mw != point["value"]:
                        old_record.power_mw = point["value"]
                        old_record.emissions = get_emissions(point["value"], psr)
                        old_record.updated_at = updated_at
                        records_to_update.append(old_record)
                else:
                    emissions = get_emissions(point["value"], psr)
                    records_to_create.append(
                        PSRGeneration(
                            start=point["start"],
                            power_mw=point["value"],
                            emissions=emissions,
                            control_area=control_area,
                            psr=psr,
                        )
                    )
            print("creating and updating")
            with transaction.atomic():
                self.bulk_create(records_to_create, batch_size=1000)
                self.bulk_update(
                    records_to_update,
                    ["power_mw", "emissions", "updated_at"],
                    batch_size=1000,
                )

    def update_emissions(self):
        records = self.all()
        to_update = []
        for record in records:
            record.emissions = get_emissions(record.power_mw, record.psr)
            to_update.append(record)

        self.bulk_update(to_update, fields=["emissions"], batch_size=1000)

    def get_emission_intensity_data(
        self, start: Optional[datetime], end: Optional[datetime]
    ):
        header = ["start", "emission_intensity"]
        timerange_query = Q()
        if start:
            timerange_query &= Q(start__gte=start)
        if end:
            timerange_query &= Q(start__lt=end)
        records = (
            self.filter(timerange_query)
            .values(
                "start",
            )
            .order_by("start")
            .annotate(
                emission_intensity=(
                    Coalesce(Sum("emissions"), 0.0) / Coalesce(Sum("power_mw"), 0.0)
                )
                * 4
            )
            .values_list(*header)
        )
        return [header] + list(records)
    
    def get_emission_intensity_data_for_region(
        self, region: Union[RegionDena, RegionNorthSouth], start: Optional[datetime]=None, end: Optional[datetime]=None
    ):
        header = ["start", f"emission_intensity_{region}"]
        timeranges = Redispatch.objects.get_timeranges(region, start, end)
        if not timeranges:
            return [header] + []
        redispatch_timerange_query = Q()
        for timerange in timeranges:
            redispatch_timerange_query |= Q(start__range=timerange)
        timerange_query = Q()
        if start:
            timerange_query &= Q(start__gte=start)
        if end:
            timerange_query &= Q(start__lt=end)
        records = (
            self.filter(timerange_query)
            .values(
                "start",
            )
            .order_by("start")
            .annotate(
                **{f"emission_intensity_{region}": models.Case(
                    models.When(redispatch_timerange_query, then=models.Value(0.0)),
                    default=(Coalesce(Sum("emissions"), 0.0) / Coalesce(Sum("power_mw"), 0.0)) * 4,
                    output_field=models.FloatField()
                )}
            )
            .values_list(*header)
        )

        return [["start", f"Emissionsintensität {RegionNorthSouth(region).label if region in RegionNorthSouth else 'dena ' + region}"]] + list(records)

    def get_generation_data(self, start: Optional[datetime], end: Optional[datetime]):
        header = ["start"] + [psr.value.upper() for psr in PSR_TYPES_POST_2024]
        timerange_query = Q()
        if start:
            timerange_query &= Q(start__gte=start)
        if end:
            timerange_query &= Q(start__lt=end)
        query = (
            self.filter(timerange_query)
            .values(
                "start",
            )
            .order_by("start")
        )
        for psr in PSR_TYPES_POST_2024:
            query = query.annotate(
                **{
                    psr.value.upper(): Coalesce(
                        Sum(
                            "power_mw",
                            filter=Q(psr=psr),
                        ),
                        0.0,
                    )
                }
            )
        records = query.values_list(*header)

        return [header] + list(records)

    def get_emissions_data(self, start: Optional[datetime], end: Optional[datetime]):
        header = ["start"] + [psr.value.upper() for psr in PSR_TYPES_POST_2024]
        timerange_query = Q()
        if start:
            timerange_query &= Q(start__gte=start)
        if end:
            timerange_query &= Q(start__lt=end)
        query = (
            self.filter(timerange_query)
            .values(
                "start",
            )
            .order_by("start")
        )
        for psr in PSR_TYPES_POST_2024:
            query = query.annotate(
                **{
                    psr.value.upper(): Coalesce(
                        Sum(
                            "emissions",
                            filter=Q(psr=psr),
                        ),
                        0.0,
                    )
                }
            )
        records = query.values_list(*header)

        return [header] + list(records)


def get_emissions(power_mw: Optional[float], psr: PsrType) -> Optional[float]:
    if power_mw is None:
        return None

    mwh = power_mw / 4  # We have values in 15-min. resolution

    return EMISSIONS_FACTORS[psr] * mwh


class PSRGeneration(models.Model):
    start = models.DateTimeField(null=False)
    control_area = models.CharField(
        verbose_name=("Control area"), max_length=16, choices=ControlArea.choices
    )
    psr = models.CharField(
        verbose_name=("PSR type"), max_length=3, choices=PsrType.choices
    )
    power_mw = models.FloatField(null=True)
    emissions = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = PSRGenerationManager()

    class Meta:
        indexes = [
            models.Index(fields=["start", "control_area", "psr"]),
            models.Index(fields=["start", "psr"]),
            models.Index(fields=["start"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["start", "control_area", "psr"],
                name="unique_psr_generation_record",
            )
        ]


EMISSIONS_FACTORS = {
    PsrType.B01: 123,  # "Biomasse"
    PsrType.B02: 1075,  # "Braunkohle"
    PsrType.B03: 1098,  # "Fossil Coal-derived gas"
    PsrType.B04: 420,  # "Erdgas"
    PsrType.B05: 933,  # "Steinkohle"
    PsrType.B06: 1098,  # "Mineralöl"
    PsrType.B07: 1098,  # "Fossil Oil shale"
    PsrType.B08: 1098,  # "Fossil Peat"
    PsrType.B09: 5,  # "Geothermie"
    PsrType.B10: 5,  # "Pumpspeicher"
    PsrType.B11: 3,  # "Wasserkraft (Laufwasser)"
    PsrType.B12: 3,  # "Wasserspeicher"
    PsrType.B13: 3,  # "Marine"
    PsrType.B14: 35,  # "Kernenergie"
    PsrType.B15: 5,  # "Sonstige Erneuerbare Energien"
    PsrType.B16: 38,  # "Photovoltaik"
    PsrType.B17: 1098,  # "Abfall"
    PsrType.B18: 9,  # "Windenergie (Offshore-Anlage)"
    PsrType.B19: 9,  # "Windenergie (Onshore-Anlage)"
    PsrType.B20: 1098,  # "Sonstige konventionelle Energien"
}
