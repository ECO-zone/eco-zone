import csv
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import reduce
import logging
from operator import add
from typing import Optional, Union
from pathlib import Path
from uuid import uuid4
from xml.etree import ElementTree

from django.db import models, transaction
from django.db.models import F, Func, Q, Sum, Avg
from django.db.models.functions import Coalesce
from django.utils import timezone

from ecozone.utils import round_date_to_quarter_hour


logger = logging.getLogger(__name__)


@dataclass
class EmissionFactorsNordSued:
    nord: Optional[float]
    sued: Optional[float]
    start: datetime


class RegionNorthSouth(models.TextChoices):
    NORTH = "north", "Nord"
    SOUTH = "south", "Süd"


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

    @classmethod
    def from_label(cls, label):
        match label:
            case "Biomasse":
                return cls.B01
            case "Braunkohle":
                return cls.B02
            case "Fossil Coal-derived gas":
                return cls.B03
            case "Erdgas":
                return cls.B04
            case "Steinkohle":
                return cls.B05
            case "Mineralöl":
                return cls.B06
            case "Fossil Oil shale":
                return cls.B07
            case "Fossil Peat":
                return cls.B08
            case "Geothermie":
                return cls.B09
            case "Pumpspeicher":
                return cls.B10
            case "Wasserkraft (Laufwasser)":
                return cls.B11
            case "Wasserspeicher":
                return cls.B12
            case "Marine":
                return cls.B13
            case "Kernenergie":
                return cls.B14
            case "Sonstige Erneuerbare Energien":
                return cls.B15
            case "Photovoltaik":
                return cls.B16
            case "Abfall":
                return cls.B17
            case "Windenergie (Offshore-Anlage)":
                return cls.B18
            case "Windenergie (Onshore-Anlage)":
                return cls.B19
            case "Sonstige konventionelle Energien":
                return cls.B20


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
        def get_clean_value(value):
            return value.strip()

        with open(Path(__file__).parent.parent / "data" / "zones_2025_01_08.csv", "r") as f:
            reader = csv.DictReader(f)
            plants_from_file = []
            for row in reader:
                name = get_clean_value(row["Name"])
                _region_north_south = get_clean_value(row["Nord-Süd"])
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
                _region_dena = get_clean_value(row["Dena Regionen"])
                region_dena: Optional[str]
                if not _region_dena:
                    region_dena = None
                else:
                    if len(_region_dena) == 2 and is_float(_region_dena[0]) and is_float(_region_dena[1]):
                        region_dena = _region_dena
                    else:
                        logger.info(f"{name} has invalid dena region '{_region_dena}'")
                        region_dena = None
                _is_renewable=get_clean_value(row["EE/nicht EE"])
                is_renewable: Optional[bool]
                if not _is_renewable:
                    is_renewable = None
                else:
                    if _is_renewable not in {"EE", "nicht EE"}:
                        logger.info(f"{name} has invalid renewable status '{_is_renewable}'")
                        is_renewable = None
                    else:
                        if _is_renewable == "EE":
                            is_renewable = True
                        else:
                            is_renewable = False
                psr_type: Optional[PsrType]
                try:
                    psr_type = PsrType.from_label(get_clean_value(row["Energieträger"]))
                except Exception:
                    psr_type = None
                unit_type = get_clean_value(row["Kraftwerksart"]).lower()
                is_heat_cogen = "heiz" in unit_type or "wärme" in unit_type
                plants_from_file.append(
                    PowerPlant(
                        name=name,
                        region_dena=region_dena,
                        region_north_south=region_north_south,
                        psr_type=psr_type,
                        is_renewable=is_renewable,
                        is_heat_cogen=is_heat_cogen
                    )
                )
            current_plants = {x.name: x for x in self.all()}
            plants_to_update = []
            plants_to_create = []
            attrs = ["region_dena", "region_north_south", "is_renewable", "psr_type", "is_heat_cogen"]
            for plant_from_file in plants_from_file:
                update = False
                current_plant = current_plants.get(plant_from_file.name)
                if not current_plant:
                    plants_to_create.append(plant_from_file)
                else:
                    for attr in attrs:
                        new_value = getattr(plant_from_file, attr)
                        if getattr(current_plant, attr) != new_value:
                            update = True
                            setattr(current_plant, attr, new_value)
                if update:
                    plants_to_update.append(current_plant)

            with transaction.atomic():
                self.bulk_update(plants_to_update, attrs, batch_size=1000)
                self.bulk_create(plants_to_create, batch_size=1000)
            
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
    psr_type = models.CharField(
        verbose_name=("PSR type"),
        max_length=3,
        choices=PsrType.choices,
        default=None,
        null=True,
    )
    is_renewable = models.BooleanField(
        verbose_name="EE Anlage",
        null=True
    )
    is_heat_cogen = models.BooleanField(
        null=True
    )
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

    def get_red_timeranges(self, region: Union[RegionDena, RegionNorthSouth], start: Optional[datetime], end: Optional[datetime]):
        """Get the timeranges when renewable redispatches occur in a given region."""
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

    def get_con_timeranges(self, region: Union[RegionDena, RegionNorthSouth], start: Optional[datetime], end: Optional[datetime]):
        """Get the timeranges when conventional redispatches occur in a given region."""
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
            .filter(direction="Wirkleistungseinspeisung erhöhen")
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

    def update_from_redispatch_records(self, redispatch_records=None):
        if not redispatch_records:
            redispatch_records = Redispatch.objects.all()
        timeseries_records = []
        starts = []
        ends = []
        for redispatch_record in redispatch_records:
            power_plant = redispatch_record.power_plant
            start = redispatch_record.start
            starts.append(start)
            end = redispatch_record.end
            ends.append(end)
            while start < end:
                power_mw = redispatch_record.power_mid_mw
                work_mwh = power_mw / 4  # NOTE: 15-min. res.
                emissions = get_emissions(work_mwh, power_plant.psr_type, power_plant.is_heat_cogen)
                emission_factor = emissions / work_mwh if work_mwh and emissions is not None else None
                timeseries_records.append(
                    TimeseriesRedispatch(
                        start=start,
                        direction=redispatch_record.direction,
                        power_mid_mw=power_mw,
                        work_mwh=work_mwh,
                        emissions=emissions,
                        emission_factor=emission_factor,
                        region_north_south=power_plant.region_north_south,
                        is_renewable=power_plant.is_renewable,
                        redispatch_id=redispatch_record.id,
                    )
                )
                start = start + timedelta(minutes=15)
        old_timeseries_records = {x.make_key(): x for x in self.filter(Q(start__gte=min(starts)) & Q(start__lt=max(ends))).all()}
        recs_to_update = []
        recs_to_create = []
        for rec in timeseries_records:
            old_rec = old_timeseries_records.get(rec.make_key())
            if old_rec:
                if old_rec.work_mwh != rec.work_mwh or old_rec.emission_factor != rec.emission_factor:
                    old_rec.work_mwh = rec.work_mwh
                    old_rec.emission = rec.emissions
                    old_rec.emission_factor = rec.emission_factor
                    recs_to_update.append(old_rec)
            else:
                recs_to_create.append(rec)
        self.bulk_create(recs_to_create, batch_size=1000)
        self.bulk_update(recs_to_update, ["work_mwh", "emissions", "emission_factor"], batch_size=1000)

        return {"start": min(starts), "end": max(ends)} if starts else None
    
    def update_missing_emission_factors(self):
        missing = TimeseriesRedispatch.objects.filter(
            emission_factor__isnull=True,
            region_north_south="south",
            is_renewable=False,
            direction="Wirkleistungseinspeisung erhöhen"
        )
        to_update = []
        for x in missing:
            power_plant = x.redispatch.power_plant
            work_mwh = x.power_mid_mw / 4  # NOTE: 15-min. res.
            emissions = get_emissions(work_mwh, power_plant.psr_type, power_plant.is_heat_cogen)
            x.emissions = emissions
            x.emission_factor = emissions / work_mwh
            to_update.append(x)
        
        self.bulk_update(to_update, ["emissions", "emission_factor"], batch_size=1000)

    def update_heat_cogen_emission_factors(self):
        records = TimeseriesRedispatch.objects.filter(redispatch__power_plant__is_heat_cogen=True).all()
        to_update = []
        for x in records:
            power_plant = x.redispatch.power_plant
            work_mwh = x.power_mid_mw / 4  # NOTE: 15-min. res.
            emissions = get_emissions(work_mwh, power_plant.psr_type, power_plant.is_heat_cogen)
            x.emissions = emissions
            x.emission_factor = emissions / work_mwh
            to_update.append(x)
        
        self.bulk_update(to_update, ["emissions", "emission_factor"], batch_size=1000)
       
    def get_timeseries_data(self, start: Optional[datetime], end: Optional[datetime]):
        if not start:
            start = (timezone.now() - timedelta(days=365)).replace(hour=0, minute=0, microsecond=0)
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

    def get_timeseries_data_x(self, start: Optional[datetime], end: Optional[datetime]):
        if not start:
            start = (timezone.now() - timedelta(days=365)).replace(hour=0, minute=0, microsecond=0)
        header = ["start", "power_mid_mw_increase"]
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
            # .annotate(
            #     power_mid_mw_decrease=Coalesce(
            #         Sum(
            #             "power_mid_mw",
            #             filter=Q(direction="Wirkleistungseinspeisung reduzieren"),
            #         ),
            #         0.0,
            #     )
            # )
            .annotate(
                power_mid_mw_increase=Coalesce(
                    Sum(
                        "power_mid_mw",
                        filter=Q(direction="Wirkleistungseinspeisung erhöhen", region_north_south="south", is_renewable=False),
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
    
    def get_north_south_redispatch_data(self, start: Optional[datetime], end: Optional[datetime]):
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
                    con_ef_north=Coalesce(
                        Sum("emissions",
                            field="emissions*work_mwh",
                            filter=Q(direction="Wirkleistungseinspeisung erhöhen") & Q(region_north_south=RegionNorthSouth.NORTH) & Q(is_renewable=False) & Q(emission_factor__isnull=False),
                            default=0.0,
                        ) / Sum(
                            "work_mwh",
                            filter=Q(direction="Wirkleistungseinspeisung erhöhen") & Q(region_north_south=RegionNorthSouth.NORTH) & Q(is_renewable=False) & Q(emission_factor__isnull=False),
                            default=1.0,
                        ),
                        0.0,
                    )
                )
            .annotate(
                con_ef_south=Coalesce(
                    Sum("emissions",
                        field="emissions*work_mwh",
                        filter=Q(direction="Wirkleistungseinspeisung erhöhen") & Q(region_north_south=RegionNorthSouth.SOUTH) & Q(is_renewable=False) & Q(emission_factor__isnull=False),
                        default=0.0,
                    ) / Sum(
                        "work_mwh",
                        filter=Q(direction="Wirkleistungseinspeisung erhöhen") & Q(region_north_south=RegionNorthSouth.SOUTH) & Q(is_renewable=False) & Q(emission_factor__isnull=False),
                        default=1.0,
                    ),
                    0.0,
                )
            )
            .values_list("start", "con_ef_north", "con_ef_south", named=True)
        )
        return records


class TimeseriesRedispatch(models.Model):
    """Note: Resolution is 15-minutes."""
    start = models.DateTimeField(null=False)
    direction = models.CharField(max_length=100, null=False)
    power_mid_mw = models.FloatField(null=False)
    work_mwh = models.FloatField(null=False)  # NOTE: Resolution is 15-minutes.
    emissions = models.FloatField(null=True)  # Can't be calculated if the PSR type of the plant is unknown
    emission_factor = models.FloatField(null=True)  # Can't be calculated if the PSR type of the plant is unknown
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

    def make_key(self):
        return f"{str(self.start.isoformat())}__{self.redispatch_id}"


class ControlArea(models.TextChoices):
    _50Hertz = "10YDE-VE-------2", "50Hertz"
    AMPRION = "10YDE-RWENET---I", "Amprion"
    TENNET = "10YDE-EON------1", "TenneT"
    TRANSNETBW = "10YDE-ENBW-----N", "TransnetBW"
    GERMANY = "10Y1001A1001A83F", "Germany"


class ForecastType(models.TextChoices):
    DAYAHEAD = "day-ahead"
    INTRADAY = "intraday"
    CURRENT = "current"


# TODO: b14 (nuclear) is not part of the dataset after 2014
PSR_TYPES_POST_2024 = [
    x
    for x in PsrType
    if x not in {PsrType.B03, PsrType.B07, PsrType.B08, PsrType.B13, PsrType.B14}
]


RENEWABLE_PSR_TYPES = [
    PsrType.B01,
    PsrType.B09,
    PsrType.B10,
    PsrType.B11,
    PsrType.B12,
    PsrType.B13,
    PsrType.B15,
    PsrType.B16,
    PsrType.B18,
    PsrType.B19,
]


CONVENTIONAL_PSR_TYPES = [x for x in PSR_TYPES_POST_2024 if x not in RENEWABLE_PSR_TYPES]


WIND_SOLAR_PSR_TYPES = [PsrType.B16, PsrType.B18, PsrType.B19]


EMISSION_INTENSITY_EXPRESSION = reduce(add, [Coalesce(F(f"{x}_em"), 0.0) for x in PSR_TYPES_POST_2024]) / reduce(add, [Coalesce(F(f"{x}_work_mwh"), 1.0) for x in PSR_TYPES_POST_2024])


WIND_SOLAR_RESIDUAL_EXPRESSION = reduce(add, [Coalesce(F(f"{x}_gen"), 0.0) for x in PSR_TYPES_POST_2024]) - reduce(add, [Coalesce(F(f"{x}_gen"), 0.0) for x in WIND_SOLAR_PSR_TYPES])


FORECAST_WIND_SOLAR_RESIDUAL_EXPRESSION = Coalesce(F("agg_gen"), 0.0) - reduce(add, [Coalesce(F(f"{x}_gen"), 0.0) for x in WIND_SOLAR_PSR_TYPES])


class GenerationManager(models.Manager):
    def update_wind_solar_residual(self, start):
        now = datetime.now(UTC)
        records = (
                    self.filter(start__gte=start)
                    .annotate(ws_residual_new=WIND_SOLAR_RESIDUAL_EXPRESSION)
                    .all()
                )
        for record in records:
            record.ws_residual = record.ws_residual_new
            record.updated_at = now
        self.bulk_update(records, fields=["ws_residual", "updated_at"], batch_size=1000)

    def update_forecasts(self):
        now = datetime.now(UTC)
        records_to_create = []
        records_to_update = []
        gen_records = {x.start: x for x in (
            self.filter(start__gte=now)
            .order_by("start")
            .all()
        )}
        forecast_records = (
            Forecast.objects.filter(start__gte=now)
            .filter(agg_gen__isnull=False)
            .filter(b16_gen__isnull=False)
            .filter(b18_gen__isnull=False)
            .filter(b19_gen__isnull=False)
            .order_by("start")
            .all()
        )
        for forecast_record in forecast_records:
            update = False
            gen_record = gen_records.get(forecast_record.start)
            if gen_record:
                gen_record.updated_at = now
                update = True
            else:
                gen_record = Generation(start=forecast_record.start)
                update = False
            nearest_neighbor = (
                self.filter(Q(start__gte=now-timedelta(days=30)) & Q(start__lte=now-timedelta(minutes=15)))
                .annotate(diff_ws_factor=Func((F("ws_residual")-forecast_record.ws_residual), function="ABS"))
                .order_by("diff_ws_factor")
                .first()
            )

            for psr_type in PSR_TYPES_POST_2024:
                gen_field = f"{psr_type}_gen"
                work_field = f"{psr_type}_work_mwh"
                em_field = f"{psr_type}_em"
                if psr_type in WIND_SOLAR_PSR_TYPES:
                    gen_value = getattr(forecast_record, gen_field)
                    work_value = gen_value / 4  # NOTE: 15-min. res.
                    em_value = get_emissions(work_value, psr_type)
                    setattr(gen_record, gen_field, gen_value)
                    setattr(gen_record, work_field, work_value)
                    setattr(gen_record, em_field, em_value)
                else:
                    gen_value = getattr(nearest_neighbor, gen_field)
                    work_value = getattr(nearest_neighbor, work_field)
                    em_value = getattr(nearest_neighbor, em_field)
                    setattr(gen_record, gen_field, gen_value)
                    setattr(gen_record, work_field, work_value)
                    setattr(gen_record, em_field, em_value)
            
            if update:
                records_to_update.append(gen_record)
            else:
                records_to_create.append(gen_record)

        print("creating and updating")
        with transaction.atomic():
            self.bulk_create(records_to_create, batch_size=1000)
            self.bulk_update(
                records_to_update,
                [f"{x}_gen" for x in PSR_TYPES_POST_2024] + [f"{x}_work_mwh" for x in PSR_TYPES_POST_2024] + [f"{x}_em" for x in PSR_TYPES_POST_2024] + ["updated_at"],
                batch_size=1000,
            )

    def update_redispatch(self, start: Optional[datetime]=None, end: Optional[datetime]=None):
        start = start if start else datetime(year=2022, month=12, day=31, hour=23, tzinfo=UTC)
        now = datetime.now(UTC) + timedelta(days=7)
        end = end if end else now
        gen_query = (
                self.filter(
                    Q(start__gte=start) & Q(start__lte=end)
                )
            )
        gen_records = {r.start: r for r in gen_query.all()}
        red_records = TimeseriesRedispatch.objects.get_north_south_redispatch_data(start, end)
        records_to_update = []
        records_to_create = []
        for red_record in red_records:
            update = False
            gen_record = gen_records.get(red_record.start)
            if gen_record:
                con_ef_north = getattr(red_record, "con_ef_north")
                if gen_record.con_ef_north != con_ef_north:
                    gen_record.con_ef_north = con_ef_north
                    update = True
                con_ef_south = getattr(red_record, "con_ef_south")
                if gen_record.con_ef_south != con_ef_south:
                    gen_record.con_ef_south = con_ef_south
                    update = True
                if update:
                    gen_record.updated_at = now
                    records_to_update.append(gen_record)
        print("updating")
        with transaction.atomic():
            self.bulk_update(
                records_to_update,
                ["con_ef_north", "con_ef_south", "updated_at"],
                batch_size=1000,
            )


    def import_records(self, xml):
        print("Starting import")
        name_spaces = {
            "entsoe": "urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0"
        }
        etree = ElementTree.fromstring(xml)
        points = []
        for entry in etree.findall("./entsoe:TimeSeries", name_spaces):
            # Only process generation records
            if entry.find("./entsoe:inBiddingZone_Domain.mRID", name_spaces) is None:
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
            )
            records_to_check = {r.start: r for r in query.all()}
            records_to_create = []
            records_to_update = []
            updated_at = datetime.now(UTC)
            for point in points:
                old_record = records_to_check.get(point["start"])
                power_mw = point["value"]
                work_mwh = power_mw / 4  # NOTE: 15-minute resolution
                emissions = get_emissions(work_mwh, psr)
                if old_record:
                    if getattr(old_record, f"{psr}_gen") != power_mw:
                        setattr(old_record, f"{psr}_gen", power_mw)
                        setattr(old_record, f"{psr}_work_mwh", power_mw)
                        setattr(old_record, f"{psr}_em", emissions)
                        old_record.updated_at = updated_at
                        records_to_update.append(old_record)
                else:
                    records_to_create.append(
                        self.model(**{
                            "start": point["start"],
                            f"{psr}_gen": power_mw,
                            f"{psr}_work_mwh": work_mwh,
                            f"{psr}_em": emissions,
                        })
                    )
            print("creating and updating")
            with transaction.atomic():
                self.bulk_create(records_to_create, batch_size=1000)
                self.bulk_update(
                    records_to_update,
                    [f"{psr}_gen", f"{psr}_work_mwh", f"{psr}_em", "updated_at"],
                    batch_size=1000,
                )
                self.update_wind_solar_residual(points[0]["start"])

    def get_emission_intensity_data(
        self, start: Optional[datetime], end: Optional[datetime]
    ):
        if not start:
            start = (timezone.now() - timedelta(days=365)).replace(hour=0, minute=0, microsecond=0)
        header = ["start", "emission_intensity"]
        timerange_query = Q()
        if start:
            timerange_query &= Q(start__gte=start)
        if end:
            timerange_query &= Q(start__lt=end)
        records = (
            self.filter(timerange_query)
            .values("start")
            .order_by("start")
            .annotate(emission_intensity=EMISSION_INTENSITY_EXPRESSION)
            .values_list(*header)
        )

        return [header] + list(records)
    
    def get_emission_intensity_data_for_region(
        self, region: Union[RegionDena, RegionNorthSouth], start: Optional[datetime]=None, end: Optional[datetime]=None
    ):
        """
        For a given region:
        1. If there is no RE redispatch in the North _or_ the South, show the national emission intensity.
        2. If there is RE redispatch in the given region, show 0 emission intensity.
        3. If there is no RE redispatch in the given region _but_ there is RE redispatch the other region,
        show the emission intensity for just the conventional plants that are being redispatched in the given region.
        """
        if not start:
            start = (timezone.now() - timedelta(days=365)).replace(hour=0, minute=0, microsecond=0)
        header = ["start", f"emission_intensity_{region}"]
        target_region = region
        other_region = RegionNorthSouth.NORTH if region == RegionNorthSouth.SOUTH else RegionNorthSouth.SOUTH
        red_timeranges_target = Redispatch.objects.get_red_timeranges(target_region, start, end)
        red_timeranges_other = Redispatch.objects.get_red_timeranges(other_region, start, end)
        con_timeranges_other = Redispatch.objects.get_con_timeranges(other_region, start, end)
        if not red_timeranges_target:
            return [header] + []
        re_target_timerange_query = Q()
        for timerange in red_timeranges_target:
            re_target_timerange_query |= Q(start__range=timerange)
        timerange_query = Q()
        if start:
            timerange_query &= Q(start__gte=start)
        if end:
            timerange_query &= Q(start__lt=end)
        re_other_timerange_query = Q()
        for timerange in red_timeranges_other:
            re_other_timerange_query |= Q(start__range=timerange)
        con_target_timerange_query = Q()
        for timerange in con_timeranges_other:
            con_target_timerange_query |= Q(start__range=timerange)
        records = (
            self.filter(timerange_query)
            .values(
                "start",
            )
            .order_by("start")
            .annotate(
                **{f"emission_intensity_{region}": models.Case(
                    models.When(re_target_timerange_query & ~con_target_timerange_query, then=models.Value(0.0)),
                    models.When(~re_target_timerange_query & re_other_timerange_query & Q(**{f"con_ef_{region}__gt": 0}), then=F(f"con_ef_{region}")),
                    default=EMISSION_INTENSITY_EXPRESSION,
                    output_field=models.FloatField()
                )}
            )
            .values_list(*header)
        )

        return [["start", f"Emissionsintensität {RegionNorthSouth(region).label if region in RegionNorthSouth else 'dena ' + region}"]] + list(records)


    def get_emission_factors_nord_sued(
        self,
    ) -> EmissionFactorsNordSued:
        """
        The emission factors will be the same if there is non-renewable redispatch in both zones
        _or_ if there is renewable dispatch in both zones. They will only differ if one and only
        one zone has renewable dispatch.
        """
        start = timezone.now()
        minutes_correction: int
        if start.minute < 15:
            minutes_correction = 0
        elif start.minute < 30:
            minutes_correction = 15
        elif start.minute < 45:
            minutes_correction = 30
        else:
            minutes_correction = 45
        start = start.replace(minute=minutes_correction, second=0, microsecond=0) - timedelta(hours=1)
        def get_value(region):
            has_renewable_redispatch = (TimeseriesRedispatch.objects.filter(start=start)
                .filter(region_north_south=region)
                .filter(direction="Wirkleistungseinspeisung reduzieren")
                .filter(is_renewable=True)
                .exists()
            )
            value: Optional[float]
            if has_renewable_redispatch:
                value = 0
            else:
                try:
                    record = (
                        self.filter(start=start)
                        .values(
                            "start",
                        )
                        .order_by("start")
                        .annotate(emissions_intensity=EMISSION_INTENSITY_EXPRESSION)
                        .last()
                    )
                    value = record["emissions_intensity"]
                except Exception:
                    value = None
            
            return value
        
        nord = get_value(RegionNorthSouth.NORTH)
        sued = get_value(RegionNorthSouth.SOUTH)

        return EmissionFactorsNordSued(nord=nord, sued=sued, start=start)


    def get_generation_data(self, start: Optional[datetime], end: Optional[datetime]):
        if not start:
            start = (timezone.now() - timedelta(days=365)).replace(hour=0, minute=0, microsecond=0)
        header = ["start"] + [psr.value.upper() for psr in PSR_TYPES_POST_2024]
        values_list = ["start"] + [f"{psr}_gen" for psr in PSR_TYPES_POST_2024]

        timerange_query = Q()
        if start:
            timerange_query &= Q(start__gte=start)
        if end:
            timerange_query &= Q(start__lt=end)
        query = (
            self.filter(timerange_query)
            # .filter(control_area=ControlArea.GERMANY)
            # .values(
            #     "start",
            # )
            .order_by("start")
        )
        # for psr in PSR_TYPES_POST_2024:
        #     query = query.annotate(
        #         **{
        #             psr.value.upper(): Coalesce(
        #                 Sum(
        #                     "power_mw",
        #                     filter=Q(psr=psr),
        #                 ),
        #                 0.0,
        #             )
        #         }
        #     )
        records = query.values_list(*values_list)

        return [header] + list(records)

    def get_emissions_data(self, start: Optional[datetime], end: Optional[datetime]):
        if not start:
            start = (timezone.now() - timedelta(days=365)).replace(hour=0, minute=0, microsecond=0)
        header = ["start"] + [psr.value.upper() for psr in PSR_TYPES_POST_2024]
        values_list = ["start"] + [f"{psr}_em" for psr in PSR_TYPES_POST_2024]
        timerange_query = Q()
        if start:
            timerange_query &= Q(start__gte=start)
        if end:
            timerange_query &= Q(start__lt=end)
        query = (
            self.filter(timerange_query)
            .order_by("start")
        )
        # for psr in PSR_TYPES_POST_2024:
        #     query = query.annotate(
        #         **{
        #             psr.value.upper(): Coalesce(
        #                 Sum(
        #                     "emissions",
        #                     filter=Q(psr=psr),
        #                 ),
        #                 0.0,
        #             )
        #         }
        #     )
        records = query.values_list(*values_list)

        return [header] + list(records)


class Generation(models.Model):
    start = models.DateTimeField(null=False)
    b01_gen = models.FloatField(null=True)
    b02_gen = models.FloatField(null=True)
    b04_gen = models.FloatField(null=True)
    b05_gen = models.FloatField(null=True)
    b06_gen = models.FloatField(null=True)
    b09_gen = models.FloatField(null=True)
    b10_gen = models.FloatField(null=True)
    b11_gen = models.FloatField(null=True)
    b12_gen = models.FloatField(null=True)
    b14_gen = models.FloatField(null=True)
    b15_gen = models.FloatField(null=True)
    b16_gen = models.FloatField(null=True)
    b17_gen = models.FloatField(null=True)
    b18_gen = models.FloatField(null=True)
    b19_gen = models.FloatField(null=True)
    b20_gen = models.FloatField(null=True)
    b01_work_mwh = models.FloatField(null=True)
    b02_work_mwh = models.FloatField(null=True)
    b04_work_mwh = models.FloatField(null=True)
    b05_work_mwh = models.FloatField(null=True)
    b06_work_mwh = models.FloatField(null=True)
    b09_work_mwh = models.FloatField(null=True)
    b10_work_mwh = models.FloatField(null=True)
    b11_work_mwh = models.FloatField(null=True)
    b12_work_mwh = models.FloatField(null=True)
    b14_work_mwh = models.FloatField(null=True)
    b15_work_mwh= models.FloatField(null=True)
    b16_work_mwh = models.FloatField(null=True)
    b17_work_mwh = models.FloatField(null=True)
    b18_work_mwh = models.FloatField(null=True)
    b19_work_mwh = models.FloatField(null=True)
    b20_work_mwh = models.FloatField(null=True)
    b01_em = models.FloatField(null=True)
    b02_em = models.FloatField(null=True)
    b04_em = models.FloatField(null=True)
    b05_em = models.FloatField(null=True)
    b06_em = models.FloatField(null=True)
    b09_em = models.FloatField(null=True)
    b10_em = models.FloatField(null=True)
    b11_em = models.FloatField(null=True)
    b12_em = models.FloatField(null=True)
    b14_em = models.FloatField(null=True)
    b15_em = models.FloatField(null=True)
    b16_em = models.FloatField(null=True)
    b17_em = models.FloatField(null=True)
    b18_em = models.FloatField(null=True)
    b19_em = models.FloatField(null=True)
    b20_em = models.FloatField(null=True)
    con_ef_north = models.FloatField(null=True)
    con_ef_south = models.FloatField(null=True)
    ws_residual = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = GenerationManager()

    class Meta:
        indexes = [
            models.Index(fields=["start"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["start"],
                name="unique_generation_record",
            )
        ]


def get_emissions(work_mwh: Optional[float], psr: PsrType, is_heat_cogen: Optional[bool]=None) -> Optional[float]:
    if work_mwh is None or psr is None:
        return None

    scaling_factor = 0.625 if is_heat_cogen else 1
    emission_factor = EMISSIONS_FACTORS[psr] * scaling_factor

    return emission_factor * work_mwh


class ForecastManager(models.Manager):

    def import_records(self, xml, forecast_type: ForecastType):
        print("Starting import")
        try:
            name_spaces = {
                "entsoe": "urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0"
            }
            etree = ElementTree.fromstring(xml)
            points = []
            for entry in etree.findall("./entsoe:TimeSeries", name_spaces):
                control_area = ControlArea(
                    entry.find("./entsoe:inBiddingZone_Domain.mRID", name_spaces).text
                )
                psr = PsrType(
                    entry.find(
                        "./entsoe:MktPSRType/entsoe:psrType", name_spaces
                    ).text.lower()
                )
                resolution = entry.find(
                    "./entsoe:Period/entsoe:resolution", name_spaces
                ).text
                if resolution != "PT15M":
                    raise Exception(f"Got unexpected resolution {resolution} for {psr} in {control_area}")
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
                if points:
                    query = (
                        self.filter(
                            Q(start__gte=points[0]["start"]) & Q(start__lte=points[-1]["start"])
                        )
                    )
                    records_to_check = {r.start: r for r in query.all()}
                    records_to_create = []
                    records_to_update = []
                    updated_at = datetime.now(UTC)
                    for point in points:
                        old_record = records_to_check.get(point["start"])
                        if old_record:
                            if getattr(old_record, f"{psr}_gen") != point["value"]:
                                # If forecast_type is current, always update
                                # If old value is null, always update
                                # Otherwise, if the forecast_types match, then update
                                # Or if the forecast_type is intraday and the old type is day-ahead
                                # if (forecast_type == ForecastType.CURRENT) or (old_record.forecast_type == forecast_type) or (forecast_type == ForecastType.INTRADAY and old_record.forecast_type == ForecastType.DAYAHEAD) or (getattr(old_record, f"{psr}_gen") is None):
                                if point["value"] is not None:
                                    setattr(old_record, f"{psr}_gen", point["value"])
                                    old_record.forecast_type = forecast_type
                                    old_record.updated_at = updated_at
                                    records_to_update.append(old_record)
                        else:
                            records_to_create.append(
                                self.model(**{
                                    "start": point["start"],
                                    f"{psr}_gen": point["value"],
                                    "forecast_type": forecast_type,
                                })
                            )
                    print("creating and updating")
                    with transaction.atomic():
                        self.bulk_create(records_to_create, batch_size=1000)
                        self.bulk_update(
                            records_to_update,
                            [f"{psr}_gen", "forecast_type", "updated_at"],
                            batch_size=1000,
                        )
                        self.update_wind_solar_residual(points[0]["start"])
        except Exception as e:
            logger.exception(str(e))

    def import_aggregate_records(self, xml):
        print("Starting import")
        try:
            name_spaces = {
                "entsoe": "urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0"
            }
            etree = ElementTree.fromstring(xml)
            for entry in etree.findall("./entsoe:TimeSeries", name_spaces):
                points = []
                control_area = ControlArea(
                    entry.find("./entsoe:inBiddingZone_Domain.mRID", name_spaces).text
                )
                resolution = entry.find(
                    "./entsoe:Period/entsoe:resolution", name_spaces
                ).text
                if resolution != "PT60M":
                    raise Exception(f"Got unexpected resolution {resolution} for {control_area}")
                start = datetime.fromisoformat(
                    entry.find(
                        "./entsoe:Period/entsoe:timeInterval/entsoe:start", name_spaces
                    ).text
                )
                for item in entry.findall(
                    "./entsoe:Period/entsoe:Point/entsoe:quantity", name_spaces
                ):
                    for _ in range(4):
                        point = {"start": start, "value": int(item.text)}
                        points.append(point)
                        start += timedelta(minutes=15)

                    # start += timedelta(minutes=15)
                    # point = {"start": start, "value": int(item.text)}
                    # points.append(point)
                    # start += timedelta(minutes=15)
                if points:
                    query = (
                        self.filter(
                            Q(start__gte=points[0]["start"]) & Q(start__lte=points[-1]["start"])
                        )
                    )
                    records_to_check = {r.start: r for r in query.all()}
                    records_to_create = []
                    records_to_update = []
                    updated_at = datetime.now(UTC)
                    for point in points:
                        old_record = records_to_check.get(point["start"])
                        if old_record:
                            if old_record.agg_gen != point["value"]:
                                old_record.agg_gen = point["value"]
                                old_record.updated_at = updated_at
                                records_to_update.append(old_record)
                        else:
                            records_to_create.append(
                                self.model(
                                    start=point["start"],
                                    agg_gen=point["value"],
                                )
                            )
                    print("creating and updating")
                    with transaction.atomic():
                        self.bulk_create(records_to_create, batch_size=1000)
                        self.bulk_update(
                            records_to_update,
                            ["agg_gen", "updated_at"],
                            batch_size=1000,
                        )
                        self.update_wind_solar_residual(start=points[0]["start"])
        except Exception as e:
            logger.exception(str(e))

    def update_wind_solar_residual(self, start):
        now = datetime.now(UTC)
        records = (
                    self.filter(start__gte=start)
                    .annotate(ws_residual_new=FORECAST_WIND_SOLAR_RESIDUAL_EXPRESSION)
                    .all()
                )
        for record in records:
            record.ws_residual = record.ws_residual_new
            record.updated_at = now
        self.bulk_update(records, fields=["ws_residual", "updated_at"], batch_size=1000)


class Forecast(models.Model):
    start = models.DateTimeField(null=False)
    forecast_type = models.CharField(
        verbose_name=("Forecast type"), max_length=9, choices=ForecastType.choices, default=ForecastType.DAYAHEAD
    )
    b16_gen = models.FloatField(null=True)
    b18_gen = models.FloatField(null=True)
    b19_gen = models.FloatField(null=True)
    agg_gen = models.FloatField(null=True)
    ws_residual = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ForecastManager()

    class Meta:
        indexes = [
            models.Index(fields=["start"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["start",],
                name="unique_forecast_record",
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
