from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys

class FunctionalTest(StaticLiveServerTestCase):

	@classmethod
	def setUpClass(cls):
		for arg in sys.argv:
			if 'liveserver' in arg:
				cls.server_url = 'http://' + arg.split('=')[1]
				return
		super().setUpClass()
		cls.server_url = cls.live_server_url

	@classmethod
	def tearDownClass(cls):
		if cls.server_url == cls.live_server_url:
			super().tearDownClass()

	def setUp(self):
		self.browser = webdriver.Firefox()
		self.browser.implicitly_wait(3)

	def tearDown(self):
		self.browser.quit()

	def check_for_row_in_list_table(self, row_text):
		table = self.browser.find_element_by_id('id_list_table')
		rows = table.find_elements_by_tag_name('tr')
		self.assertIn(row_text, [row.text for row in rows])

	def get_item_input_box(self):
		return self.browser.find_element_by_id('id_text')


class CriminalAnalysisTest(FunctionalTest):

	def test_can_access_criminal_analysis_apps_and_run_them(self):
		# Leonidas heard about a cool new online criminal analysis app.
		# He goes to check out its page
		self.browser.get(self.server_url+'/analise_criminal/')

		# At the root of the criminal analysis app he is presented with some
		# plottings, giving him a graphical view of how well (or bad) the
		# authorities are doing
		plottings_header = self.browser.find_element_by_tag_name('h2').text
		self.assertIn('Síntese de registros', plottings_header)

		# There's also a brief summary which explains what the apps are about
		summary = self.browser.find_elements_by_tag_name('h1').text
		self.assertIn('Análise Criminal', summary)

		# He notices that there are actually two apps for criminal analysis.
		# One deals with georeferring and the other with criminal reports
		apps = self.browser.find_elements_by_tag_name('h3')
		self.assertIn('Mapa', [header.txt for header in apps])
		self.assertIn('Relatório', [header.txt for header in apps])

		# He decides he'll start by checking out the georeferring app

		# He sees a heading informing him of his current place and a google map 
		# of the city of Sinop

		# Further down he sees a form, with basic and advanced options

		# He skips the advanced options, and goes straight to the basic options,
		# where he needs to input a date, and a type of crime (which defaults to
		# 'all')

		# He sees he can also pass some optional filtering data, such as
		# street, neighborhood, and hours

		# So he fills the date box with '01/01/2016' and '31/01/2016',
		# and hits enter

		# He sees that the map is updated with the records of the given period

		# He also notices that a table has been generated with details from the
		# records of the period, and above it a summary of records in the period
		# showing the total of records

		# Satisfied, he goes back to sleep.
		self.fail('finish the test!')