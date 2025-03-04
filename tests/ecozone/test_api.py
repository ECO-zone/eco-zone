from django.test import TestCase
from ninja.testing import TestClient
from ecozone.api import api
from ecozone.models import RegionNorthSouth


client = TestClient(api)


class APITestCase(TestCase):

    def test_get_timeseries_redispatch(self):
        response = client.get("/timeseries/redispatch")
        self.assertEqual(response.status_code, 200)
        self.assertIn("header", response.json())
        self.assertIn("rows", response.json())

    def test_get_timeseries_classified_redispatch(self):
        response = client.get("/timeseries/classified_redispatch")
        self.assertEqual(response.status_code, 200)
        self.assertIn("header", response.json())
        self.assertIn("rows", response.json())

    def test_get_emission_intensity(self):
        response = client.get("/timeseries/emission-intensity")
        self.assertEqual(response.status_code, 200)
        self.assertIn("header", response.json())
        self.assertIn("rows", response.json())

    def test_get_emission_intensity_for_region(self):
        # NOTE: Django-Ninja's test client should support the following syntax but the current verion (1.1.0) does not:
        # response = client.get("/timeseries/emission-intensity-zonal", params={"region": RegionNorthSouth.NORTH})
        response = client.get(
            f"/timeseries/emission-intensity-zonal?region={RegionNorthSouth.NORTH}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("header", response.json())
        self.assertIn("rows", response.json())

    def test_get_generation(self):
        response = client.get("/timeseries/generation")
        self.assertEqual(response.status_code, 200)
        self.assertIn("header", response.json())
        self.assertIn("rows", response.json())

    def test_get_emissions(self):
        response = client.get("/timeseries/emissions")
        self.assertEqual(response.status_code, 200)
        self.assertIn("header", response.json())
        self.assertIn("rows", response.json())

    def test_get_emission_factors(self):
        response = client.get("/stats/emission-factors")
        self.assertEqual(response.status_code, 200)
