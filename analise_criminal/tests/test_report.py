from django.test import TestCase

import datetime

from setup_app.models import Ocorrencia, Natureza, Cidade
from analise_criminal import report


class ReportTest(TestCase):

	def populate_db(self):
		n = Natureza.objects.create(nome="Roubo")
		c = Cidade.objects.create(nome="Sinop")

		return Ocorrencia.objects.create(
			data=datetime.date(day=1, month=1, year=2015),
			local='Local', 		 bairro='Bairro',
			via='Via', 			 numero="numero",
			latitude=1.1, 		 longitude=2.2,
			naturezas=n, hora=datetime.time(11,11,11),
			cidade=c)

	REPORT_DATA = dict(
		data_inicial_a = datetime.date(day=1, month=1, year=2015),
		data_final_a   = datetime.date(day=31, month=1, year=2015),
		data_inicial_b = datetime.date(day=1, month=2, year=2015),
		data_final_b   = datetime.date(day=28, month=2, year=2015),
		opts 		   = 'Sim',

	)

	### Tests
	def test_helper_functions(self):
		o = self.populate_db()

	def test_get_values(self):

def two_args(a,b):
	return a,b

def fn(*vals):
	return " | ".join(vals)


class reverse_iter:

	def __init__(self, lst):
		self.i = 0
		self.lst = lst

	def __iter__(self):
		return self

	def __next__(self):
		if len(self.lst) > self.i:
			return self.lst.pop()
		else:
			raise StopIteration()