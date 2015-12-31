from django.shortcuts import render
from django.http import HttpResponse

from analise_criminal.forms import MapOptionForm, MapMarkerStyleForm
from setup_app.models import Ocorrencia

def map(request):
	form_styles = MapMarkerStyleForm()
	form_options = MapOptionForm()
	o = None
	available = {
		'from': Ocorrencia.objects.first(),
		'to': Ocorrencia.objects.last()
	}
	if request.method == 'POST':
		form_options = MapOptionForm(request.POST)
		if form_options.is_valid():
			natureza = form_options.cleaned_data['natureza']
			data_inicial = form_options.cleaned_data['data_inicial']
			data_final = form_options.cleaned_data['data_final']
			o = Ocorrencia.objects.filter(natureza__contains=natureza, 
				data__gte=data_inicial,data__lte=data_final
			)
	
	context = {
		'form_options': form_options, 'form_styles': form_styles,
		'ocorrencias': o, 'availability': available
	}
	return render(request, 'analise_criminal/mapa.html', context)

def mapAjax(request):
	if request.method == 'POST':
		## not dealing with time for now
		form = MapOptionForm(data=request.POST)
		form.full_clean()

		if form.is_valid():
			natureza = form_options.cleaned_data['natureza']
			data_inicial = form_options.cleaned_data['data_inicial']
			data_final = form_options.cleaned_data['data_final']
			# Refactor: contains, not ==
			o = Ocorrencia.objects.filter(natureza__contains=natureza, 
				data__gt=data_inicial,data__lt=data_final
			)
			# Refactor: gt and lt don't include the day.
			
