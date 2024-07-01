import logging

from django.core.management.base import BaseCommand

from ecozone.harvesters.entsoe import harvest_psr_generation
from ecozone.harvesters.netztrasparenz import harvest_redispatch_to_present


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Harvest data from an external source and store it in the application database."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "data_type", nargs=1, type=str, help="The type of data to be harvested."
        )

    def handle(self, *args, **options):
        data_type = options["data_type"][0]
        try:
            match data_type:
                case "redispatch":
                    self.stdout.write(f"Harvesting {data_type}")
                    results = harvest_redispatch_to_present()
                    self.stdout.write(
                        self.style.SUCCESS(f"Harvested {results} redispatch records")
                    )
                case "psr":
                    self.stdout.write(f"Harvesting {data_type}")
                    results = harvest_psr_generation()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Harvested {results} psr generation records"
                        )
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
