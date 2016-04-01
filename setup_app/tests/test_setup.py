from django.test import TestCase
from django.db.utils import IntegrityError

import datetime
from unittest import skip

from setup_app.models import Ocorrencia



class OcorrenciaModelTest(TestCase):

	def test_can_save_new_ocorrencia(self):
		ocorr = Ocorrencia(
			data=datetime.date.today(),
			local='some place',
			bairro='some hood',
			via='some street',
			numero='some #',
			latitude=0.0,
			longitude=0.0,
			natureza='some nat',
			hora=datetime.time(11, 11, 11))
		ocorr.save()
		self.assertEqual(Ocorrencia.objects.count(), 1)

	def test_default_data(self):
		ocorr = Ocorrencia()
		self.assertEqual(ocorr.data, None)	
		self.assertEqual(ocorr.local, None)
		self.assertEqual(ocorr.bairro, None)
		self.assertEqual(ocorr.via, None)
		self.assertEqual(ocorr.numero, None)
		self.assertEqual(ocorr.latitude, 0)
		self.assertEqual(ocorr.longitude, 0)
		self.assertEqual(ocorr.natureza, '')
		self.assertEqual(ocorr.hora, None)

	@skip
	def test_cannot_save_empty_item(self):
		ocorr = Ocorrencia()
		with self.assertRaises(IntegrityError):
			ocorr.save()

	def test_string_representations(self):
		ocorr = Ocorrencia(natureza="I'm string")
		self.assertEqual(str(ocorr), "I'm string")

	def test_date_brazilian_representation(self):
		ocorr = Ocorrencia(data=datetime.date(day=1, month=1, year=2000))
		self.assertEqual(str(ocorr.date2string()), '01/01/2000')

	def test_returns_portuguese_weekday(self):
		ocorr = Ocorrencia(data=datetime.date(day=1, month=1, year=2000))
		self.assertEqual(ocorr.weekday(), 'Sábado')