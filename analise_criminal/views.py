from django.shortcuts import render
from django.http import HttpResponse

import json

from setup_app.models import Ocorrencia
from analise_criminal.forms import MapOptionForm, MapMarkerStyleForm
from analise_criminal.functions import format_data


def map(request):
	"""/analise_criminal/mapa/"""
	form_styles = MapMarkerStyleForm()
	form_options = MapOptionForm()
	
	available = {
		'from': Ocorrencia.objects.first(),
		'to': Ocorrencia.objects.last()
	}
	context = {
		'form_options': form_options, 'form_styles': form_styles,
		'availability': available
	}

	return render(request, 'analise_criminal/mapa.html', context)

def mapAjax(request):
	if request.method == 'POST':
		## not dealing with time for now
		form = MapOptionForm(data=request.POST)
		form.full_clean()
		if form.is_valid():
			natureza = form.cleaned_data['natureza']
			data_inicial = form.cleaned_data['data_inicial']
			data_final = form.cleaned_data['data_final']

			o = Ocorrencia.objects.filter(natureza__contains=natureza, 
				data__gte=data_inicial,data__lte=data_final
			)

			json_data = format_data(o)

			return HttpResponse(json_data, content_type='application/json')
		## did not test for errors yet
		else:
 	 		print(form.errors)
 	 		data = json.dumps({'errors': 'Validation error.'})
 	 		return HttpResponse(data, content_type='application/json')

