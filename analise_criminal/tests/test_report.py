from django.test import TestCase

import datetime

from setup_app.models import Ocorrencia, Natureza, Cidade
from analise_criminal.report import process_report_arguments
from analise_criminal.forms import ReportForm, ReportFilterForm
from analise_criminal.utils import conj

ROUBO = Natureza.objects.get(nome="Roubo")

class ReportTest(TestCase):

	def populate_db(self):
		n = Natureza.objects.create(pk=ROUBO.pk, nome=ROUBO.nome)
		c = Cidade.objects.create(nome="Sinop")

		return Ocorrencia.objects.create(
			data=datetime.date(day=1, month=1, year=2015),
			local='Local', 		 bairro='Bairro',
			via='Via', 			 numero="numero",
			latitude=1.1, 		 longitude=2.2,
			naturezas=n, hora=datetime.time(11,11,11),
			cidade=c)

	REPORT_FORM_DATA = {
		"data_inicial_a": datetime.date(day=1, month=1, year=2015),
		"data_final_a": datetime.date(day=31, month=1, year=2015),
		"data_inicial_b": datetime.date(day=1, month=2, year=2015),
		"data_final_b": datetime.date(day=28, month=2, year=2015),
		"opts": 'Sim'
	}

	REPORT_FORM_DATA_NO_OPTS = conj({}, REPORT_FORM_DATA, {"opts": "Não"})

	REPORT_FILTER_DATA = {
		"cidade": "1",
		"naturezas": ["Roubo"],
		"bairro": ""
	}

	def gen_forms(self, form_report, form_filter):
		form_report = ReportForm(form_report)
		form_filter = ReportFilterForm(form_filter)
		if form_report.is_valid() and form_filter.is_valid():
			return form_report, form_filter
		print("FORM REPORT:", form_report.errors or "No errors")
		print("FOMR FILTER:", form_filter.errors or "No errors")

	### Tests
	def test_report(self):
		self.populate_db()
		# report filter
		form_report, form_filter = self.gen_forms(self.REPORT_FORM_DATA_NO_OPTS,
												  self.REPORT_FILTER_DATA)
		r = process_report_arguments(form_report, form_filter)
		self.assertIn('forms', r.keys())
		self.assertIn('a', r.keys())
		self.assertIn('b', r.keys())
		self.assertIn('filtro', r.keys())
