from django.test import TestCase
from django.urls import reverse


class ViewsTestCase(TestCase):
    def test_index_view(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_usecases_view(self):
        response = self.client.get(reverse("usecases"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "usecases.html")

    def test_methodology_view(self):
        response = self.client.get(reverse("methodology"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "methodology.html")

    def test_emissions_intensity_zonal_view(self):
        response = self.client.get(reverse("emissions_intensity_zonal"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "chart.html")
        self.assertContains(response, "Emissionsintensität zonal")
        self.assertContains(response, "timeseries-emission-intensity-zonal")

    def test_redispatch_view(self):
        response = self.client.get(reverse("redispatch"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "chart.html")
        self.assertContains(response, "Redispatch-Leistung")
        self.assertContains(response, "timeseries-redispatch")

    def test_classified_redispatch_view(self):
        response = self.client.get(reverse("classified_redispatch"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "chart.html")
        self.assertContains(response, "Geordnete Redispatch-Leistung")
        self.assertContains(response, "timeseries-classified-redispatch")

    def test_emissions_intensity_germany_view(self):
        response = self.client.get(reverse("emissions_intensity_germany"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "chart.html")
        self.assertContains(response, "Emissionsintensität Deutschland")
        self.assertContains(response, "timeseries-emission-intensity")

    def test_generation_view(self):
        response = self.client.get(reverse("generation"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "chart.html")
        self.assertContains(response, "Nettostromerzeugung pro Energieträger")
        self.assertContains(response, "timeseries-generation")

    def test_emissions_view(self):
        response = self.client.get(reverse("emissions"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "chart.html")
        self.assertContains(response, "Emissionsintensität zonal")
        self.assertContains(response, "timeseries-emissions")

    def test_zone_map_view(self):
        response = self.client.get(reverse("zone_map"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "map.html")
