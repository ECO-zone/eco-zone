import logging

from django.core.management.base import BaseCommand

from ecozone.models import PowerPlant


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Update the database using data from an internal source."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "data_type", nargs=1, type=str, help="The type of data to be updated."
        )

    def handle(self, *args, **options):
        data_type = options["data_type"][0]
        try:
            match data_type:
                case "zones":
                    self.stdout.write(f"Updating {data_type}.")
                    results = PowerPlant.objects.update_zone_data()
                    self.stdout.write(
                        self.style.SUCCESS(f"Updated zone data for {results} records.")
                    )
                case _:
                    self.stderr.write(
                        self.style.ERROR(
                            f'Error: "{data_type}" is not a valid data type.'
                        )
                    )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {e}"))
            raise e
