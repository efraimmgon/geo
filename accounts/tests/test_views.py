from django.test import TestCase
from django.contrib.auth import get_user_model, SESSION_KEY
from unittest.mock import patch
from unittest import skip

from accounts.forms import LoginForm

User = get_user_model()


class LoginViewTest(TestCase):

	### Helper Functions

	def get_login_page(self):
		return self.client.get('/accounts/login/')

	def create_user_and_mock_authenticate(self, mock_authenticate):
		user = User.objects.create(username='mockuser', password='mypass')
		user.backend = ''
		mock_authenticate.return_value = user
		return user

	def login_user(self, username, password):
		return self.client.post(
			'/accounts/login/',
			data={'username': username, 'password': password}
		)

	### Tests

	def test_login_page_can_be_accessed(self):
		self.assertEqual(self.get_login_page().status_code, 200)

	def test_uses_login_template(self):
		response = self.get_login_page()
		self.assertTemplateUsed(response, 'accounts/login.html')

	def test_renders_LoginForm(self):
		response = self.get_login_page()
		self.assertIsInstance(response.context['form'], LoginForm)

	@patch('accounts.views.authenticate')
	def test_calls_authenticate(self, mock_authenticate):
		mock_authenticate.return_value = None
		self.client.post(
			'/accounts/login/', 
			data={'username': 'mockuser', 'password': 'mypass'})
		mock_authenticate.assert_called_once_with(
			username='mockuser', password='mypass'
		)

	@patch('accounts.views.authenticate')
	def test_gets_logged_in_if_authenticate_returns_user(
		self, mock_authenticate):
		user = self.create_user_and_mock_authenticate(mock_authenticate)
		self.login_user(user.username, user.password)
		self.assertEqual(self.client.session[SESSION_KEY], str(user.pk))

	@patch('accounts.views.authenticate')
	def test_redirects_to_homepage_if_login_successful(
		self, mock_authenticate):
		user = self.create_user_and_mock_authenticate(mock_authenticate)
		response = self.login_user(user.username, user.password)
		self.assertRedirects(response, '/analise_criminal/')

	@patch('accounts.views.authenticate')
	def test_redirects_to_next_url_if_available(self, mock_authenticate):
		url = '/accounts/login/?next=/analise_criminal/relatorio/'
		user = self.create_user_and_mock_authenticate(mock_authenticate)
		response = self.client.post(
			url,
			data={'username': user.username, 'password': user.password}
		)
		self.assertRedirects(response, '/analise_criminal/relatorio/')
