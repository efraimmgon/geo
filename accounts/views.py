from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from accounts.forms import LoginForm

def user_login(request):
	error = None
	form = LoginForm()

	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)

		if user:
			if user.is_active:
				login(request, user)
				return redirect('/analise_criminal/')
			else:
				return HttpResponse('Sua conta está desabilitada.')
		else:
			error = "Login inválido usando: %s, %s" % (username, password,)
	
	return render(request, 'login.html', {'error': error, 'form': form})

@login_required
def user_logout(request):
	logout(request)
	return redirect('/accounts/login/')