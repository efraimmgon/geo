from selenium.webdriver.common.keys import Keys
from .base import FunctionalTest

class EscalaTest(FunctionalTest):

	def test_escala_app(self):
		# Ferri goes to the app index
		self.browser.get(self.server_url + '/escala/')
		
		# He's presented with a dashboard from where he can controls
		# the escala's actions
		header = self.browser.find_element_by_tag_name('h1')
		self.assertIn('Centro de Controle', header.text)

		# He starts by populating the database with the name of the troopers.
		# He clicks a button which opens a csv file, iteraters through its 
		# rows and inserts the name, personal-id, and rank of the trooper
		finder = self.browser.find_element_by_id('select-file').click()
		finder.send_keys('/Users/efraimmgon/boilerplate/escala.csv').send_keys(
			Keys.ENTER)

		self.wait_for_element_with_id('id_force_map')

		# Satisfied, he goes back to his ebay shit.