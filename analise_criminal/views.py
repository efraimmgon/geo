from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Min, Max, Count
from django.contrib.auth.decorators import login_required

import json, unicodedata

from setup_app.models import Ocorrencia
from analise_criminal.forms import (
	MapOptionForm, AdvancedOptionsForm, MapMarkerStyleForm,
	ReportForm,
)
from analise_criminal.functions import (
	format_data, process_map_arguments, get_percentage,
)


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


@login_required
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

		# comparação a/b
		# variação dado a em relação ao dado b, e vice-versa
		# a
		furto1 = o1.filter(natureza__contains='furto').values(
			'natureza').annotate(num=Count('id'))[0]
		roubo1 = o1.filter(natureza__contains='roubo').values(
			'natureza').annotate(num=Count('id'))[0]
		uso1 = o1.filter(natureza__contains='uso il').values(
			'natureza').annotate(num=Count('id'))[0]
		homicidio1 = o1.filter(natureza__contains='dio doloso').values(
			'natureza').annotate(num=Count('id'))[0]
		search = unicodedata.normalize('NFKD', 'Tráfico Ilícito de Drogas')
		trafico1 = o1.filter(natureza=search).values(
			'natureza').annotate(num=Count('id'))[0]
		# b
		furto2 = o2.filter(natureza__contains='furto').values(
			'natureza').annotate(num=Count('id'))[0]
		roubo2 = o2.filter(natureza__contains='roubo').values(
			'natureza').annotate(num=Count('id'))[0]
		uso2 = o2.filter(natureza__contains='uso il').values(
			'natureza').annotate(num=Count('id'))[0]
		homicidio2 = o2.filter(natureza__contains='dio doloso').values(
			'natureza').annotate(num=Count('id'))[0]
		search = unicodedata.normalize('NFKD', 'Tráfico Ilícito de Drogas')
		trafico2 = o2.filter(natureza=search).values(
			'natureza').annotate(num=Count('id'))[0]
		# percentage variation from a to b
		percent_furto = get_percentage(furto1['num'], furto2['num'])
		percent_roubo = get_percentage(roubo1['num'], roubo2['num'])
		percent_uso = get_percentage(uso1['num'], uso2['num'])
		percent_homicidio = get_percentage(
			homicidio1['num'], homicidio2['num']
		)
		percent_trafico = get_percentage(
			trafico1['num'], trafico2['num']
		)

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

		context['comparison'] = [
			{'a': furto1, 'b': furto2, 'variation': percent_furto},
			{'a': roubo1, 'b': roubo2, 'variation': percent_roubo},
			{'a': homicidio1, 'b': homicidio2, 'variation': percent_homicidio},
			{'a': trafico1, 'b': trafico2, 'variation': percent_trafico},
			{'a': uso1, 'b': uso2, 'variation': percent_uso},
		]

		context['form'] = form

		return render(request, 'analise_criminal/relatorio.html', context)
	else:
		return render(request, 'analise_criminal/relatorio.html', {'form': 
			form})

