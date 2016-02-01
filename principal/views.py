from django.shortcuts import render


def index(request):
	return render(request, 'index.html')

def biblioteca(request):
	return render(request, 'biblioteca.html')