from datetime import datetime, timedelta, UTC

import pytest

from django.test import TestCase
from django.utils import timezone

from ecozone.harvesters.netztrasparenz import harvest_redispatch
from ecozone.models import (
    get_emissions,
    Generation,
    PowerPlant,
    PsrType,
    PSR_TYPES_POST_2024,
)


class DataTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        PowerPlant.objects.update_zone_data()
        start = datetime(2024, 12, 31, 0, 0, 0, tzinfo=UTC)
        end = datetime(2025, 1, 3, 11, 45, 0, tzinfo=UTC)
        generation_records = []
        while start <= end:
            params = {"start": start}
            for psr_type in PSR_TYPES_POST_2024:
                gen = 100
                work_mwh = gen / 4
                emissions = get_emissions(work_mwh, psr_type)
                params[f"{psr_type}_gen"] = gen
                params[f"{psr_type}_work_mwh"] = work_mwh
                params[f"{psr_type}_em"] = emissions
            generation_records.append(Generation(**params))
            start = start + timedelta(minutes=15)
        Generation.objects.bulk_create(generation_records, batch_size=1000)
        harvest_redispatch(file="./data/redispatch_2025-01-01--2025-01-02.csv")
        cls.results = Generation.objects.get_emission_intensity_data_for_region(
            "south", datetime(2024, 12, 31, 0, 0, 0, tzinfo=UTC), end
        )[1:]
        cls.start_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)


class GenerationModelTestCase(DataTestCase):

    def test_generation_creation(self):
        generation = Generation.objects.get(start=self.start_time)
        self.assertEqual(generation.start, self.start_time)
        self.assertEqual(generation.b01_gen, 100.0)
        self.assertEqual(generation.b01_work_mwh, 25.0)
        self.assertEqual(generation.b01_em, 3075.0)
        self.assertEqual(generation.con_ef_north, 0.0)
        self.assertEqual(generation.con_ef_south, 0.0)
        self.assertEqual(generation.ws_residual, None)

    def test_get_emission_intensity_data(self):
        start = self.start_time
        end = self.start_time + timedelta(days=1)
        data = Generation.objects.get_emission_intensity_data(start, end)
        # get_emission_intensity_data filters by start time gte and end time lt.
        # So, the end time is not included in the results. We expect 96 results
        # (24*4 for 15 min. resolution).
        self.assertEqual(len(data), 97)  # header + 96 records
        self.assertEqual(data[0], ["start", "emission_intensity"])
        self.assertEqual(data[1][0], self.start_time)
        self.assertIsInstance(data[1][1], float)

    def test_get_emission_intensity_data_for_region(self):
        start = self.start_time
        end = self.start_time + timedelta(days=1)
        data = Generation.objects.get_emission_intensity_data_for_region(
            "north", start, end
        )
        # get_emission_intensity_data_for_region filters by start time gte and end time lt.
        # So, the end time is not included in the results. We expect 96 results
        # (24*4 for 15 min. resolution).
        self.assertEqual(len(data), 97)  # header + 96 record
        self.assertEqual(
            data[0],
            ["start", "Emissionsintensität Nord", "Emissionsintensität Deutschland"],
        )
        self.assertEqual(data[1][0], self.start_time)
        self.assertIsInstance(data[1][1], float)
        self.assertIsInstance(data[1][2], float)

    def test_get_emission_factors_nord_sued(self):
        factors = Generation.objects.get_emission_factors_nord_sued(self.start_time)
        self.assertIsInstance(factors.nord, (float, int))
        self.assertIsInstance(factors.sued, (float, int))
        self.assertIsInstance(factors.start, datetime)

    def test_get_generation_data(self):
        start = self.start_time
        end = self.start_time + timedelta(days=1)
        data = Generation.objects.get_generation_data(start, end)
        # get_generation_data filters by start time gte and end time lt.
        # So, the end time is not included in the results. We expect 96 results
        # (24*4 for 15 min. resolution).
        self.assertEqual(len(data), 97)  # header + 96 records
        self.assertEqual(data[0][0], "start")
        self.assertEqual(data[1][0], self.start_time)
        self.assertIsInstance(data[1][1], float)

    def test_get_emissions_data(self):
        start = self.start_time
        end = self.start_time + timedelta(days=1)
        data = Generation.objects.get_emissions_data(start, end)
        # get_emissions_data filters by start time gte and end time lt.
        # So, the end time is not included in the results. We expect 96 results
        # (24*4 for 15 min. resolution).
        self.assertEqual(len(data), 97)  # header + 96 record
        self.assertEqual(data[0][0], "start")
        self.assertEqual(data[1][0], self.start_time)
        self.assertIsInstance(data[1][1], float)

    def test_get_emissions(self):
        work_mwh = 25.0
        psr = PsrType.B01
        emissions = get_emissions(work_mwh, psr)
        self.assertIsInstance(emissions, float)
        self.assertEqual(emissions, 123 * work_mwh)


class ZonalEmissionFactorTestCase(DataTestCase):

    def test_emission_factor_is_zero_when_res_redispatch_south(self):
        """
        Emission factor is zero when there's RES redispatch in south, meaning:
            1. There is RES Wirkleistung reduzieren in the south.
            2. There is no conventional Wirkleistung erhöhen in the south.
        """
        start = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
        end = datetime(2025, 1, 1, 16, 0, 0, tzinfo=UTC)
        for i in self.results:
            if i[0] > start and i[0] < end:
                assert i[1] == 0

    def test_emission_factor_is_national_value_when_no_res_or_con_redispatches_in_south(
        self,
    ):
        """
        Emission factor is the German national value when there are no
        RES or conventional redispatches in the south.
        """
        # Period when there is RES redispatch in south.
        # We don't expect the national value during this period,
        # but it might appear outside it.
        res_start = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
        res_end = datetime(2025, 1, 1, 16, 0, 0, tzinfo=UTC)

        # Period when there is RES redispatch in the north BUT
        # there is no conventional Wirkleistung erhöhen in the south.
        # In this case, we expect the national value as there are no
        # relevant conventional redispatch emissions to consider.
        nat_start = res_end
        nat_end = datetime(2025, 1, 1, 18, 0, 0, tzinfo=UTC)

        for i in self.results:
            if i[0] < res_start or (i[0] > nat_start and i[0] < nat_end):
                assert i[1] == 394.8

    def test_emission_factor_is_redispatch_value_when_con_redispatch_in_south(self):
        """
        Emission factor is derived from the conventional redispatch values
        when there's conventional dispatch in south, meaning:
            1. All the criteria for RES redispatch in the south are not met.
            2. There's RES Wirkleistunung reduzieren in the north.
            3. There's no con Wirkleistung erhöhen in the north.
            4. There's con Wirkleistung erhöhen in the south (otherwise, there
               would be no redispatch values to use for the emission factor).
        """
        start = datetime(2025, 1, 1, 18, 0, 0, tzinfo=UTC)
        end = datetime(2025, 1, 1, 20, 0, 0, tzinfo=UTC)
        for i in self.results:
            if i[0] > start and i[0] < end:
                assert i[1] == 583.125
