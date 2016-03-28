from django.test import TestCase


class CriminalAnalysisPageTest(TestCase):

	def test_criminal_analysis_page_renders_index_template(self):
		response = self.client.get('/analise_criminal/')
		self.assertTemplateUsed(response, 'index.html')