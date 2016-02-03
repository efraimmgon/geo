from django.shortcuts import render

from principal.models import ExternalSource, Tag


def index(request):
	return render(request, 'index.html')

def biblioteca(request):
	context = {
		'sources': ExternalSource.objects.all(),
		'tags': Tag.objects.all(),
	}
	return render(request, 'biblioteca.html', context)