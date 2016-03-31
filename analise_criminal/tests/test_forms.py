from django.test import TestCase

import datetime

from setup_app.models import Ocorrencia
from analise_criminal.forms import (
	MapOptionForm, AdvancedOptionsForm, MapMarkerStyleForm, ReportForm,
	ReportFilterForm,
)
from analise_criminal.report import FURTO, ROUBO, USO, HOM, TRAFICO


class MapOptionsFormTest(TestCase):

	def test_form_renders_input_fields(self):
		form = MapOptionForm()
		## natures
		self.assertIn('name="natureza"', form.as_p())
		self.assertIn('value=""', form.as_p())
		self.assertIn('value="todas"', form.as_p())
		self.assertIn('value="'+FURTO+'"', form.as_p())
		self.assertIn('value="'+ROUBO+'"', form.as_p())
		self.assertIn('value="drogas"', form.as_p())
		self.assertIn('value="'+USO+'"', form.as_p())
		self.assertIn('value="'+TRAFICO+'"', form.as_p())
		self.assertIn('value="'+HOM+'"', form.as_p())
		self.assertIn('value="'+HOM+' culposo'+'"', form.as_p())
		self.assertIn('value="'+HOM+' doloso'+'"', form.as_p())
		## dates
		self.assertIn('name="data_inicial"', form.as_p())
		self.assertIn('name="data_final"', form.as_p())
		self.assertIn('placeholder="dd/mm/aaaa"', form.as_p())

	def test_form_validation_for_blank_fields(self):
		form = MapOptionForm(data={
			'natureza': '', 
			'data_inicial': datetime.date.today(),
			'data_final': datetime.date.today(),
			})
		self.assertFalse(form.is_valid())
		form = MapOptionForm(data={
			'natureza': 'todas', 
			'data_inicial': '',
			'data_final': datetime.date.today(),
			})
		self.assertFalse(form.is_valid())
		form = MapOptionForm(data={
			'natureza': 'todas', 
			'data_inicial': datetime.date.today(),
			'data_final': '',
			})
		self.assertFalse(form.is_valid())

# end of MapOptionFormTest

class AdvancedOptionsFormTest(TestCase):

	def test_form_renders_input_fields(self):
		form = AdvancedOptionsForm()
		self.assertIn('name="bairro"', form.as_p())
		self.assertIn('name="via"', form.as_p())
		self.assertIn('name="hora_inicial"', form.as_p())
		self.assertIn('name="hora_final"', form.as_p())
		self.assertIn('placeholder="hh:mm"', form.as_p())

	def test_form_fields_are_optional(self):
		form = AdvancedOptionsForm(data={
			'bairro': '',
			'via': '',
			'hora_inicial': '',
			'hora_final': ''
			})
		self.assertTrue(form.is_valid())


class MapMarkerStyleFormTest(TestCase):

	def test_form_renders_option_fields(self):
		form = MapMarkerStyleForm()
		self.assertIn('value="basicMarker"', form.as_p())
		self.assertIn('value="heatmap"', form.as_p())


class ReportFormTest(TestCase):

	def test_form_renders_input_fields(self):
		form = ReportForm()
		self.assertIn('placeholder="dd/mm/aaaa"', form.as_p())
		self.assertIn('name="data_inicial_a"', form.as_p())
		self.assertIn('name="data_final_a"', form.as_p())
		self.assertIn('name="data_inicial_b"', form.as_p())
		self.assertIn('name="data_final_b"', form.as_p())
		self.assertIn('name="opts"', form.as_p())

	def test_form_validation_for_required_fields(self):
		## dates
		today = datetime.date.today()
		data1 = {'data_inicial_a': '', 'data_final_a': today, 
		'data_inicial_a': today, 'data_final_b': today}
		data2 = {'data_inicial_a': today, 'data_final_a': '', 
		'data_inicial_a': today, 'data_final_b': today}
		data3 = {'data_inicial_a': today, 'data_final_a': today, 
		'data_inicial_a': '', 'data_final_b': today}
		data4 = {'data_inicial_a': today, 'data_final_a': today, 
		'data_inicial_a': today, 'data_final_b': ''}
		self.assertFalse(ReportForm(data=data1).is_valid())
		self.assertFalse(ReportForm(data=data2).is_valid())
		self.assertFalse(ReportForm(data=data3).is_valid())
		self.assertFalse(ReportForm(data=data4).is_valid())


class ReportFilterTest(TestCase):

	def test_form_renders_checkbox_fields(self):
		form = ReportFilterForm()
		## naturezas is multiple choice
		self.assertIn('name="naturezas"', form.as_p())
		self.assertIn('name="bairro"', form.as_p())
		## detail is multiple choice
		self.assertIn('name="details"', form.as_p())
		self.assertIn('value="weekdays"', form.as_p())
		self.assertIn('value="time"', form.as_p())



