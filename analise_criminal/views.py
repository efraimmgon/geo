from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Min, Max, Count
from django.contrib.auth.decorators import login_required

import json, unicodedata

from setup_app.models import Ocorrencia
from analise_criminal.forms import (
	MapOptionForm, AdvancedOptionsForm, MapMarkerStyleForm,
	ReportForm
)
from analise_criminal.functions import format_data, process_map_arguments


def index(request):
	return render(request, 'analise_criminal/index.html')

@login_required
def map(request):
	"""/analise_criminal/mapa/"""
	form_styles = MapMarkerStyleForm()
	form_options = MapOptionForm()
	form_advanced_options = AdvancedOptionsForm()

	queryset = Ocorrencia.objects.all() 
	mindata = queryset.aggregate(Min('data'))
	maxdata = queryset.aggregate(Max('data'))

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
			natureza = unicodedata.normalize(
				'NFKD', form.cleaned_data['natureza']
			)
			data_inicial = form.cleaned_data['data_inicial']
			data_final = form.cleaned_data['data_final']
			hora_inicial = form_advanced.cleaned_data['hora_inicial']
			hora_final = form_advanced.cleaned_data['hora_final']
			bairro = unicodedata.normalize(
				'NFKD', form_advanced.cleaned_data['bairro']
			)
			via = unicodedata.normalize(
				'NFKD', form_advanced.cleaned_data['via']
			)

			o = process_map_arguments(natureza, data_inicial, data_final,
				bairro, via, hora_inicial, hora_final)

			json_data = format_data(o)
		else:
			## refactor forms.py to have portuguese errors.
 	 		json_data = json.dumps({'errors': form.errors})
	
	return HttpResponse(json_data, content_type='application/json')


def report(request):
	form = ReportForm()
	context = {'form': form}
	return render(request, 'analise_criminal/relatorio.html', context)


def make_report(request):
	form = ReportForm(data=request.GET)
	context = {}
	stat = {}
	if form.is_valid():
		data_inicial_a = form.cleaned_data['data_inicial_a']
		data_final_a = form.cleaned_data['data_final_a']
		data_inicial_b = form.cleaned_data['data_inicial_b']
		data_final_b = form.cleaned_data['data_final_b']

		o1 = Ocorrencia.objects.filter(
			data__gte=data_inicial_a, data__lte=data_final_a
		)
		o2 = Ocorrencia.objects.filter(
			data__gte=data_inicial_b, data__lte=data_final_b
		)

		# a
		naturezas1 = o1.values('natureza').annotate(num=Count('id'))
		naturezas1 = naturezas1.order_by('-num')[:5]
		bairros1 = o1.values('bairro').annotate(num=Count('id'))
		bairros1 = bairros1.order_by('-num')[:5]
		vias1 = o1.values('via').annotate(num=Count('id'))
		vias1 = vias1.order_by('-num')[:10]
		bairros_vias1 = o1.values('bairro', 'via').annotate(num=Count('id'))
		bairros_vias1 = bairros_vias1.order_by('-num')[:10]
		dom1 = o1.filter(data__week_day=1)
		seg1 = o1.filter(data__week_day=2)
		ter1 = o1.filter(data__week_day=3)
		qua1 = o1.filter(data__week_day=4)
		qui1 = o1.filter(data__week_day=5)
		sex1 = o1.filter(data__week_day=6)
		sab1 = o1.filter(data__week_day=7)

		# b
		naturezas2 = o2.values('natureza').annotate(num=Count('id'))
		naturezas2 = naturezas2.order_by('-num')[:5]
		bairros2 = o2.values('bairro').annotate(num=Count('id'))
		bairros2 = bairros2.order_by('-num')[:5]
		vias2 = o2.values('via').annotate(num=Count('id'))
		vias2 = vias2.order_by('-num')[:10]
		bairros_vias2 = o2.values('bairro', 'via').annotate(num=Count('id'))
		bairros_vias2 = bairros_vias2.order_by('-num')[:10]
		dom2 = o2.filter(data__week_day=1)
		seg2 = o2.filter(data__week_day=2)
		ter2 = o2.filter(data__week_day=3)
		qua2 = o2.filter(data__week_day=4)
		qui2 = o2.filter(data__week_day=5)
		sex2 = o2.filter(data__week_day=6)
		sab2 = o2.filter(data__week_day=7)

		context['a'] = {
			'total': o1.count(),
			'naturezas': naturezas1,
			'bairros': bairros1,
			'vias': vias1,
			'b_v': bairros_vias1,
			'dias': [dom1, seg1, ter1, qua1, qui1, sex1, sab1],
		}

		context['b'] = {
			'total': o2.count(),
			'naturezas': naturezas2,
			'bairros': bairros2,
			'vias': vias2,
			'b_v': bairros_vias2,
			'dias': [dom2, seg2, ter2, qua2, qui2, sex2, sab2],
		}

		context['form'] = form

		return render(request, 'analise_criminal/relatorio.html', context)
	else:
		return render(request, 'analise_criminal/relatorio.html', {'form': 
			form})

