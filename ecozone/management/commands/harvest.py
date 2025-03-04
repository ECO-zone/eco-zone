import logging
import sys

from django.core.management.base import BaseCommand

from ecozone.harvesters.entsoe import (
    harvest_aggregate_generation_forecast,
    harvest_psr_generation,
    harvest_renewable_generation_forecast,
)
from ecozone.harvesters.netztrasparenz import harvest_redispatch
from ecozone.models import ForecastType


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Harvest data from an external source and store it in the application database."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "data_type", nargs=1, type=str, help="The type of data to be harvested."
        )
        parser.add_argument(
            "--forecast_type",
            nargs=1,
            type=str,
            help="The type of forecast to be harvested.",
        )
        parser.add_argument(
            "--historical",
            action="store_true",
            help="Harvest historical data, updating existing data if necessary.",
        )

    def handle(self, *args, **options):
        data_type = options["data_type"][0]
        historical = options["historical"]
        try:
            match data_type:
                case "redispatch":
                    self.stdout.write(f"Harvesting {data_type}.")
                    if historical:
                        self.stdout.write(f'Ignoring "--historical" flag.')
                    results = harvest_redispatch()
                    self.stdout.write(
                        self.style.SUCCESS(f"Harvested {results} redispatch records.")
                    )
                case "psr":
                    self.stdout.write(f"Harvesting {data_type}.")
                    if historical:
                        self.stdout.write(
                            "Historical data will be updated if necessary."
                        )
                    results = harvest_psr_generation(historical)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Harvested {results} psr generation records."
                        )
                    )
                case "renewable_forecast":
                    try:
                        forecast_type = ForecastType(options["forecast_type"][0])
                    except Exception:
                        self.stderr(
                            "forecast_type is required when harvesting renewable_forecast."
                        )
                        sys.exit(1)
                    self.stdout.write(f"Harvesting {data_type}.")
                    results = harvest_renewable_generation_forecast(forecast_type)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Harvested {results} renewable generation forecast records."
                        )
                    )
                case "aggregate_forecast":
                    self.stdout.write(f"Harvesting {data_type}.")
                    results = harvest_aggregate_generation_forecast()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Harvested {results} renewable generation forecast records."
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
