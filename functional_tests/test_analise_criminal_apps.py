from .base import FunctionalTest


class CriminalAnalysisRootTest(FunctionalTest):

	def test_can_access_criminal_analysis_root_page(self):
		# Leonidas heard about a cool new online criminal analysis app.
		# He goes to check out its page
		self.browser.get(self.server_url+'/analise_criminal/')

		# At the root of the criminal analysis app he is presented with some
		# plottings, giving him a graphical view of how well (or bad) the
		# authorities are doing
		plottings_header = self.browser.find_element_by_tag_name('h2').text
		self.assertIn('Síntese de registros', plottings_header)

		# There's also a brief summary which explains what the apps are about
		summary = self.browser.find_element_by_tag_name('h1').text
		self.assertIn('Análise Criminal', summary)

		# He notices that there are actually two apps for criminal analysis.
		# One deals with georeferring and the other with criminal reports
		apps = self.browser.find_elements_by_tag_name('h3')
		self.assertIn('Mapa', [header.text for header in apps])
		self.assertIn('Relatório', [header.text for header in apps])



class GeoreferringTest(FunctionalTest):

	def test_can_access_and_run_map_app(self):
		# He decides he'll start by checking out the georeferring app
		self.browser.get('http://localhost:8000/analise_criminal/mapa/')
		# He sees a heading informing him of his current place and a google 
		# map of the city of Sinop
		main_header = self.browser.find_element_by_tag_name('h1').text
		self.assertIn("Georreferenciamento", main_header)
		gmap = self.browser.find_element_by_id('map').text
		self.assertNotEqual(len(gmap), 0)

		# There are a field with configurations settings for the map
		map_settings = self.browser.find_element_by_id('appSettings').text
		self.assertIn('Configurações', map_settings)

		# Further down he sees a form, with basic options
		options = self.browser.find_elements_by_tag_name('h4')
		self.assertIn('Básicas', [header.text for header in options])

		# Beneath it is a header saying 'Avançadas', that drops down as
		# he clicks on it, showing other optional options
		self.assertIn('Avançadas', [header.text for header in options])

		# He skips the advanced options, and goes straight to the basic 
		# options, where he needs to input a date, and a type of crime 
		nature = self.browser.find_element_by_id('id_natureza').text.split('\n')
		init_date = self.browser.find_element_by_id('id_data_inicial')
		end_date = self.browser.find_element_by_id('id_data_final')

		# These fields show some helpful messages about the input format
		self.assertIn('Selecione', nature)
		self.assertEqual(
			init_date.get_attribute('placeholder'),
			'dd/mm/aaaa')
		self.assertEqual(
			end_date.get_attribute('placeholder'),
			'dd/mm/aaaa')

		# He sees he can also pass some optional filtering data, such as
		# street, neighborhood, and hours
		hood = self.browser.find_element_by_id('id_bairro')
		street = self.browser.find_element_by_id('id_via')
		init_hour = self.browser.find_element_by_id('id_hora_inicial')
		end_hour = self.browser.find_element_by_id('id_hora_final')

		# They also show some helpful messages
		self.assertEqual(
			init_hour.get_attribute('placeholder'),
			'hh:mm')
		self.assertEqual(
			end_hour.get_attribute('placeholder'),
			'hh:mm')

		# He selects all records
		nature = self.browser.find_element_by_id('id_natureza')
		nature.find_element_by_xpath('.//option[@value="todas"]').click()

		# So he fills the date box with '01/01/2016' and '31/01/2016',
		# and hits enter
		data_inicial_input = self.browser.find_element_by_id('id_data_inicial')
		data_inicial_input.send_keys('01/01/2016')
		data_final_input = self.browser.find_element_by_id('id_data_final')
		data_final_input.send_keys('31/01/2016')

		elForm = self.browser.find_element_by_id('ocorrenciasForm')
		elForm.submit()

		# He sees that the map is updated with the records of the given period
		## <How the fuck do I check that?>

		# He also notices that a table has been generated with details from the
		# records of the period, and above it a summary of records in the 
		# period showing the total of records
		table = self.browser.find_element_by_class_name('sortable')
		summary = self.browser.find_element_by_id('id_info')
		self.assertNotEqual(len(summary.text), 0)

		# Satisfied, he goes back to sleep.