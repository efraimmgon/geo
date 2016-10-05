from django.shortcuts import render, redirect

from datetime import timedelta

from principal.models import ExternalSource, Tag
from principal.forms import TimeDeltaForm


def index(request):
	return render(request, 'index.html')

def biblioteca(request):
	context = {
		'sources': ExternalSource.objects.all(),
		'tags': Tag.objects.all(),
		'tags_and_sources': ExternalSource.objects.filter(tags__in=Tag.objects.all())
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

def utilitarios(request):
	"""Directory page to utilities"""
	context = {}
	form_timedelta = TimeDeltaForm()
	## Withdrawal app
	if 'data_inicial' in request.GET:
		form_timedelta = TimeDeltaForm(data=request.GET)
		if form_timedelta.is_valid():
			data_inicial = form_timedelta.cleaned_data['data_inicial']
			dias = form_timedelta.cleaned_data['dias']
			if dias < 1:
				pass
			else:
				data_final = data_inicial + timedelta(days=dias - 1)
				context['result_timedelta'] = {
					'inicial': data_inicial, 'final': data_final, 'timedelta': dias
				}
	context['form'] = {'timedelta': form_timedelta}

	return render(request, 'utilitarios.html', context)
