import logging

from django.db import migrations


logger = logging.getLogger(__name__)


def add_zone_info(apps, schema_editor):
    PowerPlant = apps.get_model("ecozone", "PowerPlant")
    TimeseriesRedispatch = apps.get_model("ecozone", "TimeseriesRedispatch")
    plants = PowerPlant.objects.all()
    for plant in plants:
        print(plant.name)
        records = list(TimeseriesRedispatch.objects.filter(redispatch__power_plant_id=plant.id).all())
        for record in records:
            record.region_north_south = plant.region_north_south
            record.is_renewable = plant.is_renewable
        TimeseriesRedispatch.objects.bulk_update(records, ["region_north_south", "is_renewable"], batch_size=1000)


def revert(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('ecozone', '0008_timeseriesredispatch_is_renewable_and_more'),
    ]

    operations = [
        migrations.RunPython(add_zone_info, revert, elidable=True),
    ]
