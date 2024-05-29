import logging
from uuid import uuid4

from django.db import models


logger = logging.getLogger(__name__)


class GridRegionManager(models.Manager):

    def get_dict_of_names_to_ids(self):
        return {x["name"]: x["id"] for x in self.values("name", "id").all()}


class GridRegion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=30)
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
    name = models.CharField(max_length=30)
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


class PowerPlantManager(models.Manager):

    def get_dict_of_names_to_ids(self):
        return {x["name"]: x["id"] for x in self.values("name", "id").all()}


class PowerPlant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=30)
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


class RedispatchManager(models.Manager):
    pass


class Redispatch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    start = models.DateTimeField(null=False)
    end = models.DateTimeField(null=False)
    grid_regions = models.ManyToManyField(GridRegion)
    reason = models.CharField(max_length=30, null=False)
    direction = models.CharField(max_length=40, null=False)
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
