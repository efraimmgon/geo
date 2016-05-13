from django.contrib.auth import get_user_model
from selenium.webdriver.support.ui import WebDriverWait
from django.contrib.auth.backends import ModelBackend
from unittest import skip

from .base import FunctionalTest

User = get_user_model()

class backend(object):
	def authenticate(self, **credentials):
		return User.objects.get(username=credentials['username'])
@skip
class LoginTest(FunctionalTest):

	def setUp(self):
		user = User.objects.create(username='mockuser', password='mypass')
		user.backend = backend()
		super().setUp()
	
	### Helper functions

	def wait_for_element_with_id(self, element_id):
		WebDriverWait(self.browser, timeout=30).until(
			lambda b: b.find_element_by_id(element_id)
		)

	def test_login_page(self):
		print('Count -->', User.objects.count())
		print('User -->', User.objects.get(username='mockuser'))
		# Leonidas goes to the homepage of Criminal Analysis and notices
		# a "Login" link for the first time
		self.browser.get(self.server_url)
		self.browser.find_element_by_id('id_login').click()

		# The link takes him to a login page, where he logs in with
		# his username and password
		login_header = self.browser.find_element_by_tag_name('h1').text
		self.assertIn('Login', login_header)
		self.browser.find_element_by_id('id_username').send_keys('mockuser')
		self.browser.find_element_by_id('id_password').send_keys('mypass')
		elButton = self.browser.find_element_by_css_selector('.btn')
		elButton.click()

		# He is redirected to the homepage, and he can see he is logged in
		import time
		time.sleep(5)
		self.assertEqual(self.browser.current_url, '/')
		self.wait_for_element_with_id('id_logout')
		navbar = self.find_element_by_css_selector('.navbar')
		self.assertIn('mockuser', navbar.text)