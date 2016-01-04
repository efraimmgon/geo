from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Min, Max
from django.contrib.auth.decorators import login_required

import json

from setup_app.models import Ocorrencia
from analise_criminal.forms import (
	MapOptionForm, AdvancedOptionsForm, MapMarkerStyleForm
)
from analise_criminal.functions import format_data


def index(request):
	return render(request, 'analise_criminal/index.html')

@login_required
def map(request):
	"""/analise_criminal/mapa/"""
	form_styles = MapMarkerStyleForm()
	form_options = MapOptionForm()
	form_advanced_options = AdvancedOptionsForm()

	mindata = Ocorrencia.objects.all().aggregate(Min('data'))
	maxdata = Ocorrencia.objects.all().aggregate(Max('data'))

	context = {
		'form_options': form_options, 'form_styles': form_styles,
		'form_advanced': form_advanced_options,
		'min': mindata['data__min'].strftime('%d/%m/%Y'), 
		'max': maxdata['data__max'].strftime('%d/%m/%Y')
	}

	return render(request, 'analise_criminal/mapa.html', context)

def mapAjax(request):
	if request.method == 'POST':
		form = MapOptionForm(data=request.POST)
		form_advanced = AdvancedOptionsForm(data=request.POST)
		form.full_clean()
		form_advanced.full_clean()
		if form.is_valid() and form_advanced.is_valid():
			natureza = form.cleaned_data['natureza']
			data_inicial = form.cleaned_data['data_inicial']
			data_final = form.cleaned_data['data_final']
			hora_inicial = form_advanced.cleaned_data['hora_inicial']
			hora_final = form_advanced.cleaned_data['hora_final']
			bairro = form_advanced.cleaned_data['bairro']
			via = form_advanced.cleaned_data['via']

			if natureza == 'todas':
				o = Ocorrencia.objects.filter(
					data__gte=data_inicial, data__lte=data_final
				)
			else:
				o = Ocorrencia.objects.filter(natureza=natureza, 
					data__gte=data_inicial, data__lte=data_final
				)

			if bairro:
				o = o.filter(bairro__contains=bairro)
			if via:
				o = o.filter(via__contains=via)
			if hora_inicial:
				o = o.filter(hora__gte=hora_inicial)
			if hora_final:
				o = o.filter(hora__lte=hora_final)

			json_data = format_data(o)
		else:
			## refactor forms.py to have portuguese errors.
 	 		json_data = json.dumps({'errors': form.errors})
	
	return HttpResponse(json_data, content_type='application/json')

