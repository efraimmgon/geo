from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from accounts.forms import LoginForm

INVALID_LOGIN_MESSAGE = "Login inválido. Cheque seu nome de usuário e senha."

def user_login(request):
	error = None
	if request.method == 'POST':
		user = authenticate(username=request.POST.get('username'),
					 		password=request.POST.get('password'))
		print(user.backend)
		if user:
			if user.is_active:
				login(request, user)
				return redirect('analise_criminal:index')
		else:
			error = 'QUER MERDA CARAUI'
	context = {'form': LoginForm(), 'error': error}
	return render(request, 'accounts/login.html', context)

def user_login2(request):
	error = None
	if request.method == 'POST':
		user = authenticate(username=request.POST.get('username'),
					 		password=request.POST.get('password'))
		if user and user.is_active:
			login(request, user)
			return redirect('analise_criminal:index')
		error = INVALID_LOGIN_MESSAGE
	context = {'form': LoginForm(), 'error': error}
	return render(request, 'accounts/login.html', context)

@login_required
def user_logout(request):
	logout(request)
	return redirect('accounts:login')