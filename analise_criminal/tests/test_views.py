from django.test import TestCase
from unittest import skip
import datetime
import json

from setup_app.models import Ocorrencia
from analise_criminal.forms import (
	MapOptionForm, AdvancedOptionsForm, MapMarkerStyleForm,
)
from analise_criminal.functions import process_map_arguments, format_data


class CriminalAnalysisPageTest(TestCase):

	def test_criminal_analysis_page_renders_index_template(self):
		response = self.client.get('/analise_criminal/')
		self.assertTemplateUsed(response, 'analise_criminal/index.html')


class LabPageTest(TestCase):
	pass

@skip
class MapPageTest(TestCase):

	def get_map_page(self):
		Ocorrencia.objects.create(data=datetime.date.today())
		return self.client.get('/analise_criminal/mapa/')

	### Tests

	# I'm skipping tests for login_required pages... It seems
	# I can't run them without creating a mock user to log in

	def test_map_page_can_be_accessed(self):
		response = self.get_map_page()
		self.assertEqual(response.status_code, 200)

	def test_map_page_renders_map_template(self):
		response = self.get_map_page()
		self.assertTemplateUsed(response, 'analise_criminal/mapa.html')

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

	### helper functions

	def populate_db(self):
		return Ocorrencia.objects.create(
			data=datetime.date(day=1, month=1, year=2015),
			local='Local',
			bairro='Bairro',
			via='Via',
			numero="numero",
			latitude=1.1,
			longitude=2.2,
			natureza="natureza",
			hora=datetime.time(11,11,11))

	def post_basic_data(self):
		return self.client.post('/analise_criminal/mapAjax/', data={
			'natureza': 'todas',
			'data_inicial': '01/01/2015',
			'data_final': '31/01/2015'
		})

	### tests

	def test_response_is_None_for_GET(self):
		with self.assertRaises(ValueError):
			self.client.get('/analise_criminal/mapAjax/')

	def test_response_content_type_is_json(self):
		self.populate_db()
		response = self.post_basic_data()
		self.assertIn(b'application/json', response.serialize_headers())

	def test_response_content_is_valid_json(self):
		self.populate_db()
		response = self.post_basic_data()
		try:
			json.loads(response.content.decode())
		except ValueError:
			self.fail("Returned value isn't valid json")

	###  process_map_arguments' tests

	def test_format_data_function_returns_list_of_dicts(self):
		self.populate_db()
		data = format_data(Ocorrencia.objects.all())
		self.assertIsInstance(data, list)
		self.assertIsInstance(data[0], dict)
	
	def test_can_process_map_argument_func_returns_filtered_data(self):
		self.populate_db()
		form_basic = MapOptionForm(data={
			'natureza': 'todas',
			'data_inicial': datetime.date(day=1, month=1, year=2015),
			'data_final': datetime.date(day=31, month=1, year=2015)
		})
		form_advanced = AdvancedOptionsForm(data={
			'hora_inicial': '', 'hora_final': '', 'bairro': '', 'via': ''
		})
		form_basic.full_clean()
		form_advanced.full_clean()
		data = process_map_arguments(form_basic, form_advanced)
		self.assertNotEqual(data[0].get('pk', 'false'), 'false')
		self.assertNotEqual(data[0].get('natureza', 'false'), 'false')
		self.assertNotEqual(data[0].get('bairro', 'false'), 'false')
		self.assertNotEqual(data[0].get('via', 'false'), 'false')
		self.assertNotEqual(data[0].get('numero', 'false'), 'false')
		self.assertNotEqual(data[0].get('formatted_date', 'false'), 'false')
		self.assertNotEqual(data[0].get('weekday', 'false'), 'false')
		self.assertNotEqual(data[0].get('hora', 'false'), 'false')
		self.assertNotEqual(data[0].get('latitude', 'false'), 'false')
		self.assertNotEqual(data[0].get('longitude', 'false'), 'false')




