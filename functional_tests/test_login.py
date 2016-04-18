import time
from selenium.webdriver.support.ui import WebDriverWait

from .base import FunctionalTest


class LoginTest(FunctionalTest):

	### Helper functions

	def wait_for_element_with_id(self, element_id):
		WebDriverWait(self.browser, timeout=30).until(
			lambda b: b.find_element_by_id(element_id)
		)

	def test_login_page(self):
		# Leonidas goes to the homepage of Criminal Analysis and notices
		# a "Login" link for the first time
		self.browser.get(self.server_url)
		self.browser.find_element_by_id('id_login').click()

		# The link takes him to a login page, where he logs in with
		# his username and password
		login_header = self.browser.find_element_by_tag_name('h1').text
		self.assertIn('Login', login_header)
		self.browser.find_element_by_id('id_username').send_keys('mockuser')
		self.browser.find_element_by_id('id_password').send_keys('123456')
		elButton = self.browser.find_element_by_css_selector('.btn')
		elButton.click()

		# He is redirected to the homepage, and he can see he is logged in
		self.assertEqual(self.browser.current_url, '/')
		self.wait_for_element_with_id('id_logout')
		navbar = self.find_element_by_css_selector('.navbar')
		self.assertIn('mockuser', navbar.text)