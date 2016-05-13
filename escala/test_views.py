from django.test import TestCase

ESCALA_INDEX_URL = '/escala/'

class EscalaViewsTest(TestCase):

	def test_escala_index_renders_template(self):
		response = self.client.get(ESCALA_INDEX_URL)
		self.assertTemplateUsed(response, 'escala/index.html')