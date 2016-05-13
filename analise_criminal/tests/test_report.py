from django.test import TestCase

import datetime

from setup_app.models import Ocorrencia
from analise_criminal.report import process_report_arguments


class ReportTest(TestCase):

	def populate_db(self):
		return Ocorrencia.objects.create(
			data=datetime.date(day=1, month=1, year=2015),
			local='Local', 		 bairro='Bairro',
			via='Via', 			 numero="numero",
			latitude=1.1, 		 longitude=2.2,
			natureza="natureza", hora=datetime.time(11,11,11))

	REPORT_DATA = dict(
		data_inicial_a = datetime.date(day=1, month=1, year=2015),
		data_final_a   = datetime.date(day=31, month=1, year=2015),
		data_inicial_b = datetime.date(day=1, month=2, year=2015),
		data_final_b   = datetime.date(day=28, month=2, year=2015),
		opts 		   = 'Sim',

	)

	### Tests
