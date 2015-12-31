from django.test import TestCase

from setup_app.models import Ocorrencia

class SetupTest(TestCase):
	
	def test_default_text(self):
		ocorrencia = Ocorrencia()
		self.assertEqual(ocorrencia.natureza, '')

	def test_retrieves_first_Ocorrencia(self):