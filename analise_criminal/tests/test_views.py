from django.test import TestCase
from unittest import skip


class CriminalAnalysisPageTest(TestCase):

	def test_criminal_analysis_page_renders_index_template(self):
		response = self.client.get('/analise_criminal/')
		self.assertTemplateUsed(response, 'index.html')


class LabPageTest(TestCase):
	pass


class MapPageTest(TestCase):

	def test_map_page_can_be_accessed(self):
		response = self.client.get('/analise_criminal/mapa/')
		self.assertEqual(response.status_code, 200)

	def test_map_page_renders_map_template(self):
		response = self.client.get('/analise_criminal/mapa/')
		self.assertTemplateUsed(response, 'mapa.html')


class MapAjaxTest(TestCase):
	pass