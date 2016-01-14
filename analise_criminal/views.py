from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Min, Max, Count
from django.contrib.auth.decorators import login_required

import json, unicodedata
from collections import defaultdict, namedtuple

from setup_app.models import Ocorrencia
from analise_criminal.forms import (
	MapOptionForm, AdvancedOptionsForm, MapMarkerStyleForm,
	ReportForm, ReportFilterForm
)
from analise_criminal.functions import (
	format_data, process_map_arguments, get_percentage,
	get_value, get_values, get_comparison_data, get_time,
	fetch_data
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
	form_report = ReportForm()
	form_filter = ReportFilterForm()

	context = {'form_report': form_report, 'form_filter': form_filter}
	return render(request, 'analise_criminal/relatorio.html', context)


@login_required
def make_report(request):
	form_report = ReportForm(data=request.GET)
	form_filter = ReportFilterForm(data=request.GET)
	context = {}
	Response = namedtuple('Response', ['field', 'num', 'type'])
	if form_report.is_valid() and form_filter.is_valid():
		data_inicial_a = form_report.cleaned_data['data_inicial_a']
		data_final_a = form_report.cleaned_data['data_final_a']
		data_inicial_b = form_report.cleaned_data['data_inicial_b']
		data_final_b = form_report.cleaned_data['data_final_b']

		o1 = Ocorrencia.objects.filter(
			data__gte=data_inicial_a, data__lte=data_final_a
		)
		o2 = Ocorrencia.objects.filter(
			data__gte=data_inicial_b, data__lte=data_final_b
		)

		lst_a = list(o1)
		lst_b = list(o2)

		# a
		naturezas1 = get_value(o1, 'natureza', limit=5)
		bairros1 = get_value(o1.exclude(bairro=None), 'bairro', limit=5)
		vias1 = get_value(o1.exclude(via=None), 'via', limit=10)
		locais1 = get_values(
			o1.exclude(bairro=None).exclude(via=None), 'bairro', 'via', 5
		)
		weekdays1 = []
		for i in range(1, 8):
			d = o1.filter(data__week_day=i)
			d = Response(d[0].data, d.count(), 'Dia da semana')
			weekdays1.append(d)


		# b
		naturezas2 = get_value(o2, 'natureza', limit=5)
		bairros2 = get_value(o2.exclude(bairro=None), 'bairro', limit=5)
		vias2 = get_value(o2.exclude(via=None), 'via', limit=10)
		locais2 = get_values(
			o2.exclude(bairro=None).exclude(via=None), 'bairro', 'via', 5
		)
		weekdays2 = []
		for i in range(1, 8):
			d = o2.filter(data__week_day=i)
			d = Response(d[0].data, d.count(), 'Dia da semana')
			weekdays2.append(d)

		# comparação a/b
		# variação dado a em relação ao dado b, e vice-versa
		# a
		furto1 = get_comparison_data(o1, 'Furto')
		roubo1 = get_comparison_data(o1, 'Roubo')
		uso1 = get_comparison_data(
			o1, unicodedata.normalize('NFKD', 'Uso Ilícito de Drogas'))
		homicidio_d1 = get_comparison_data(
			o1, unicodedata.normalize('NFKD', 'Homicídio Doloso'))
		homicidio_c1 = get_comparison_data(
			o1, unicodedata.normalize('NFKD', 'Homicídio Culposo'))
		trafico1 = get_comparison_data(
		 	o1, unicodedata.normalize('NFKD', 'Tráfico Ilícito de Drogas'))

		# b
		furto2 = get_comparison_data(o2, 'Furto')
		roubo2 = get_comparison_data(o2, 'Roubo')
		uso2 = get_comparison_data(
			o2, unicodedata.normalize('NFKD', 'Uso Ilícito de Drogas'))
		homicidio_d2 = get_comparison_data(
			o2, unicodedata.normalize('NFKD', 'Homicídio Doloso'))
		homicidio_c2 = get_comparison_data(
			o2, unicodedata.normalize('NFKD', 'Homicídio Culposo'))
		trafico2 = get_comparison_data(
		 	o2, unicodedata.normalize('NFKD', 'Tráfico Ilícito de Drogas'))

		# hora
		mad1, mat1, vesp1, noturno1 = get_time(lst_a)
		mad2, mat2, vesp2, noturno2 = get_time(lst_b)

		mad1 = Response('00:00 - 05:59', len(mad1), 'Horário')
		mat1 = Response('06:00 - 11:59', len(mat1), 'Horário')
		vesp1 = Response('12:00 - 17:59', len(vesp1), 'Horário')
		noturno1 = Response('18:00 - 23:59', len(noturno1), 'Horário')
		mad2 = Response('00:00 - 05:59', len(mad2), 'Horário')
		mat2 = Response('06:00 - 11:59', len(mat2), 'Horário')
		vesp2 = Response('12:00 - 17:59', len(vesp2), 'Horário')
		noturno2 = Response('18:00 - 23:59', len(noturno2), 'Horário')

		horarios1 = [mad1, mat1, vesp1, noturno1]
		horarios2 = [mad2, mat2, vesp2, noturno2]
		
		# percentage variation from a to b
		percent_total = get_percentage(o1.count(), o2.count())
		percent_furto = get_percentage(furto1['num'], furto2['num'])
		percent_roubo = get_percentage(roubo1['num'], roubo2['num'])
		percent_uso = get_percentage(uso1['num'], uso2['num'])
		percent_homicidio_d = get_percentage(
			homicidio_d1['num'], homicidio_d2['num'])
		percent_homicidio_c = get_percentage(
			homicidio_c1['num'], homicidio_c2['num'])
		percent_trafico = get_percentage(
			trafico1['num'], trafico2['num'])

		data_a = data_inicial_a.strftime('%d-%m-%Y') 
		data_a += ' a ' + data_final_a.strftime('%d-%m-%Y')
		data_b = data_inicial_b.strftime('%d-%m-%Y')
		data_b += ' a ' + data_final_b.strftime('%d-%m-%Y')
		context['data'] = {
			'a': data_a,
			'b': data_b,
		}
		context['total'] = {'a': o1.count(), 'b': o2.count(), 'variation': percent_total}
		context['dias'] = [
			weekdays1,
			weekdays2
		]

		context['basico'] = [
			{'5 ocorrências com maior registro': [naturezas1, naturezas2]},
			{'5 bairros com maior registro': [bairros1, bairros2]},
			{'10 vias com maior registro': [vias1, vias2]},
			{'5 locais com maior registro': [locais1, locais2]},
			{'Registros por dia da semana': [weekdays1, weekdays2]},
			{'Registros por horário': [horarios1, horarios2]},
		]

		context['comparison'] = [
			{'a': furto1, 'b': furto2, 'variation': percent_furto},
			{'a': roubo1, 'b': roubo2, 'variation': percent_roubo},
			{'a': homicidio_d1, 'b': homicidio_d2, 'variation': percent_homicidio_d},
			{'a': homicidio_c1, 'b': homicidio_c2, 'variation': percent_homicidio_c},
			{'a': trafico1, 'b': trafico2, 'variation': percent_trafico},
			{'a': uso1, 'b': uso2, 'variation': percent_uso},
		]

		# filter natureza
		if form_filter.cleaned_data['naturezas']:
			context['filtro'] = {}
			for natureza in form_filter.cleaned_data['naturezas']:
				natureza = unicodedata.normalize('NFKD', natureza)
				context['filtro'][natureza] = [
					{'5 bairros com maior registro': []},
					{'10 vias com maior registro': []},
					{'5 locais com maior registro': []},
					{'Registros por dia da semana': []},
					{'Registros por horário': []}
				]
				current = context['filtro'][natureza]
				for registros in [o1.filter(natureza__contains=natureza),
					o2.filter(natureza__contains=natureza)]:
					bairros = get_value(
					registros.exclude(bairro=None), 'bairro', 5)
					vias = get_value(registros.exclude(via=None), 'via', 10)
					locais = get_values(
						registros.exclude(bairro=None).exclude(via=None), 
						'bairro', 'via', 5)
					weekdays = []
					for i in range(1, 8):
						d = registros.filter(data__week_day=i)
						try:
							d = Response(d[0].data, d.count(), 'Dia da semana')
						except IndexError:
							continue
						weekdays.append(d)

					mad, mat, vesp, noturno = get_time(registros)
					mad = Response('00:00 - 05:59', len(mad), 'Horário')
					mat = Response('06:00 - 11:59', len(mat), 'Horário')
					vesp = Response('12:00 - 17:59', len(vesp), 'Horário')
					noturno = Response('18:00 - 23:59', len(noturno), 'Horário')
					horarios = [mad, mat, vesp, noturno]
					
					current[0]['5 bairros com maior registro'] += [bairros]
					current[1]['10 vias com maior registro'] += [vias]
					current[2]['5 locais com maior registro'] += [locais]
					current[3]['Registros por dia da semana'] += [weekdays]
					current[4]['Registros por horário'] += [horarios]


		context['form_report'] = form_report
		context['form_filter'] = form_filter
	else:
		context = {'form_report': form_report, 'form_filter': form_filter}
	
	return render(request, 'analise_criminal/relatorio.html', context)
