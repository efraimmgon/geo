from django.shortcuts import render, redirect

from principal.models import ExternalSource, Tag


def index(request):
	return render(request, 'index.html')

def biblioteca(request):
	context = {
		'sources': ExternalSource.objects.all(),
		'tags': Tag.objects.all(),
	}
	return render(request, 'biblioteca.html', context)

def track_url(request, source_id):
	"""
	Takes an ExternalSource.pk as arg; if the pk is valid,
	the page gets redirected to the corresponding ExternalSource.url,
	else the page is redirected to the index.
	"""
	if source_id:
		try:
			e = ExternalSource.objects.get(pk=source_id)
			e.views += 1
			e.save()
			return redirect(e.url)
		except ExternalSource.DoesNotExist:
			pass
	return redirect('principal:index')