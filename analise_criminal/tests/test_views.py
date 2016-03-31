from django.test import TestCase
from unittest import skip
import datetime

from setup_app.models import Ocorrencia
from analise_criminal.forms import (
	MapOptionForm, AdvancedOptionsForm, MapMarkerStyleForm,
)


class CriminalAnalysisPageTest(TestCase):

	def test_criminal_analysis_page_renders_index_template(self):
		response = self.client.get('/analise_criminal/')
		self.assertTemplateUsed(response, 'index.html')


class LabPageTest(TestCase):
	pass


class MapPageTest(TestCase):

	def get_map_page(self):
		Ocorrencia.objects.create(data=datetime.date.today())
		return self.client.get('/analise_criminal/mapa/')

	def test_map_page_can_be_accessed(self):
		response = self.get_map_page()
		self.assertEqual(response.status_code, 200)

	def test_map_page_renders_map_template(self):
		response = self.get_map_page()
		self.assertTemplateUsed(response, 'mapa.html')

	def test_uses_MapOptionForm(self):
		response = self.get_map_page()
		self.assertIsInstance(
			response.context['forms']['basic_options'], MapOptionForm)

	def test_uses_AdvancedOptionsForm(self):
		response = self.get_map_page()
		self.assertIsInstance(
			response.context['forms']['advanced_options'], AdvancedOptionsForm)

	def test_uses_MapMarkerStyleForm(self):
		response = self.get_map_page()
		self.assertIsInstance(
			response.context['forms']['marker_styles'], MapMarkerStyleForm)

	def test_passes_min_and_max_dates(self):
		Ocorrencia.objects.create(data=datetime.date(day=1, month=1, year=2000))
		response = self.get_map_page()
		self.assertEqual(
			response.context['min'], '01/01/2000')
		self.assertEqual(
			response.context['max'], datetime.date.today().strftime('%d/%m/%Y'))

# end of MapPageTest



class MapAjaxTest(TestCase):
	pass