"""
- Functions from the report and make_report func from analise_criminal.views
"""

from django.db.models import Count

from datetime import time
from unicodedata import normalize
from collections import namedtuple, OrderedDict

from setup_app.models import Ocorrencia

Response = namedtuple('Response', ['field', 'num', 'type'])
monthnames = {
	1: 'Janeiro',
	2: 'Fevereiro',
	3: 'Março',
	4: 'Abril',
	5: 'Maio',
	6: 'Junho',
	7: 'Julho',
	8: 'Agosto',
	9: 'Setembro',
	10: 'Outubro',
	11: 'Novembro',
	12: 'Dezembro'
}

weekdays = {
	0: 'Segunda-feira',
	1: 'Terça-feira',
	2: 'Quarta-feira',
	3: 'Quinta-feira',
	4: 'Sexta-feira',
	5: 'Sábado',
	6: 'Domingo'
}

weekdays_django = {
	1: 'Domingo',
	2: 'Segunda-feira',
	3: 'Terça-feira',
	4: 'Quarta-feira',
	5: 'Quinta-feira',
	6: 'Sexta-feira',
	7: 'Sábado',
}

def process_report_arguments(form_report, form_filter):
	"""
	Uses user's selections to decide what analysis to process,
	and what data to present.
	"""
	context = {}

	context['form_report'] = form_report
	context['form_filter'] = form_filter

	data_inicial_a = form_report.cleaned_data['data_inicial_a']
	data_final_a = form_report.cleaned_data['data_final_a']
	data_inicial_b = form_report.cleaned_data['data_inicial_b']
	data_final_b = form_report.cleaned_data['data_final_b']

	context['data'] = {
		'a': [data_inicial_a, data_final_a],
		'b': [data_inicial_b, data_final_b],
	}

	o1 = Ocorrencia.objects.filter(
		data__gte=data_inicial_a, data__lte=data_final_a
	)
	o2 = Ocorrencia.objects.filter(
		data__gte=data_inicial_b, data__lte=data_final_b
	)

	context['total'] = {
		'a': o1.count(), 'b': o2.count()
	}

	if form_report.cleaned_data['opts'] == 'Sim':
		# A
		a, comparison1, horarios1 = process_args(o1, compare=True)
		naturezas1, bairros1, vias1, locais1, weekdays1 = a
		furto1, roubo1, uso1, homicidio_d1, homicidio_c1, trafico1 = comparison1
		months1, xaxis1, yaxis1 = make_graphs(months=get_months(o1))

		# B
		b, comparison2, horarios2 = process_args(o2, compare=True)
		naturezas2, bairros2, vias2, locais2, weekdays2 = b
		furto2, roubo2, uso2, homicidio_d2, homicidio_c2, trafico2 = comparison2
		months1, xaxis2, yaxis2 = make_graphs(months=get_months(o2))

		context['axis'] = OrderedDict()
		if len(months1) > 2 or len(months2) > 2:
			context['axis']['total'] = [
				{'x': xaxis1, 'y': yaxis1, 'id': 'id_total_graph_a',
				'color': 'rgb(255,0,0)', 'name': 'Período A'},
				{'x': xaxis2, 'y': yaxis2, 'id': 'id_total_graph_a',
				'color': 'rgb(255,255,0)', 'name': 'Período B'}
			]

		_, wd_xaxis1, wd_yaxis1 = make_graphs(weekdays=weekdays1)
		_, wd_xaxis2, wd_yaxis2 = make_graphs(weekdays=weekdays2)
		context['axis']['Dias da semana'] = [
			{'x': wd_xaxis1, 'y': wd_yaxis1, 'id': 'id_weekday_graph_a',
			'color': 'rgb(255,0,0)', 'name': 'Período A'},
			{'x': wd_xaxis2, 'y': wd_yaxis2, 'id': 'id_weekday_graph_a',
			'color': 'rgb(255,255,0)', 'name': 'Período B'},
		]

		nat_xaxis1, nat_yaxis1 = get_axis(naturezas1)
		nat_xaxis2, nat_yaxis2 = get_axis(naturezas2)
		context['axis']['Naturezas'] = [
			{'x': nat_xaxis1, 'y': nat_yaxis1, 'id': 'id_natureza_graph_a',
			'color': 'rgb(255,0,0)', 'name': 'Período A'},
			{'x': nat_xaxis2, 'y': nat_yaxis2, 'id': 'id_natureza_graph_a',
			'color': 'rgb(255,255,0)', 'name': 'Período B'},
		]

		bairro_xaxis1, bairro_yaxis1 = get_axis(bairros1)
		bairro_xaxis2, bairro_yaxis2 = get_axis(bairros2)
		context['axis']['Bairros'] = [
			{'x': bairro_xaxis1, 'y': bairro_yaxis1, 'id': 'id_bairro_graph_a',
			'color': 'rgb(255,0,0)', 'name': 'Período A'},
			{'x': bairro_xaxis2, 'y': bairro_yaxis2, 'id': 'id_bairro_graph_a',
			'color': 'rgb(255,255,0)', 'name': 'Período B'},
		]

		via_xaxis1, via_yaxis1 = get_axis(vias1)
		via_xaxis2, via_yaxis2 = get_axis(vias2)
		context['axis']['Vias'] = [
			{'x': via_xaxis1, 'y': via_yaxis1, 'id': 'id_via_graph_a',
			'color': 'rgb(255,0,0)', 'name': 'Período A'},
			{'x': via_xaxis2, 'y': via_yaxis2, 'id': 'id_via_graph_a',
			'color': 'rgb(255,255,0)', 'name': 'Período B'},
		]

		hora_xaxis1, hora_yaxis1 = get_axis(horarios1)
		hora_xaxis2, hora_yaxis2 = get_axis(horarios2)
		context['axis']['Horários'] = [
			{'x': hora_xaxis1, 'y': hora_yaxis1, 'id': 'id_hora_graph_a',
			'color': 'rgb(255,0,0)', 'name': 'Período A'},
			{'x': hora_xaxis2, 'y': hora_yaxis2, 'id': 'id_hora_graph_a',
			'color': 'rgb(255,255,0)', 'name': 'Período B'},
		]

		# Percentage fluctuation from A to B
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

		context['total']['variation'] = percent_total

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

	if form_filter.cleaned_data['naturezas']:
		context['filtro'] = {}
		for natureza in form_filter.cleaned_data['naturezas']:
			natureza = normalize('NFKD', natureza)
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
				(_, bairros, vias, locais, wd), _, horarios = process_args(
					registros, compare=False)
				values = [bairros, vias, locais, wd, horarios]
				for i in range(len(current)):
					for key in current[i].keys():
						current[i][key] += [values[i]]

	if form_filter.cleaned_data['bairro']:
		bairro = normalize('NFKD', form_filter.cleaned_data['bairro'])
		(naturezas1, _, vias1, _, weekdays1), _, horarios1 = process_args(
			o1.filter(bairro__icontains=bairro), compare=False)
		(naturezas2, _, vias2, _, weekdays2), _, horarios2 = process_args(
			o2.filter(bairro__icontains=bairro), compare=False)

		context['bairro_detail'] = bairro
		context['detail'] = [
			{'5 ocorrências com maior registro': [naturezas1, naturezas2]},
			{'10 vias com maior registro': [vias1, vias2]},
			{'Registros por dia da semana': [weekdays1, weekdays2]},
			{'Registros por horário': [horarios1, horarios2]},
		]
	if form_filter.cleaned_data['details']:
		if 'weekdays' in form_filter.cleaned_data['details']:
			context['weekday_detail'] = OrderedDict()
			for i in range(1, 8):
				context['weekday_detail'][weekdays_django[i]] = [
					{'5 naturezas com maior registro': []},
					{'5 bairros com maior registro': []},
					{'10 vias com maior registro': []},
					{'5 locais com maior registro': []},
					{'Registros por horário': []}
				]
				current = context['weekday_detail'][weekdays_django[i]]
				for periodo in [o1, o2]:
					(naturezas, bairros, vias, locais, _), _, horarios = process_args(
						periodo.filter(data__week_day=i), compare=False)
					values = [naturezas, bairros, vias, locais, horarios]
					print(horarios)
					for j in range(len(current)):
						for key in current[j].keys():
							current[j][key] += [values[j]]

	return context


def process_args(queryset, compare=False):
	"""Process arguments for a given queryset"""
	lst = list(queryset)

	naturezas = get_value(queryset, 'natureza', limit=5)
	bairros = get_value(queryset.exclude(bairro=None), 'bairro', limit=5)
	vias = get_value(queryset.exclude(via=None), 'via', limit=10)
	locais = get_values(
		queryset.exclude(bairro=None).exclude(via=None), 'bairro', 'via', 5
	)
	weekdays = get_weekdays(queryset)

	## Comparison A/B
	# data fluctuation of a in relation to b, and vice-versa
	comparison = []
	if compare:
		furto = get_comparison_data(queryset, 'Furto')
		roubo = get_comparison_data(queryset, 'Roubo')
		uso = get_comparison_data(
			queryset, normalize('NFKD', 'Uso Ilícito de Drogas'))
		homicidio_d = get_comparison_data(
			queryset, normalize('NFKD', 'Homicídio Doloso'))
		homicidio_c = get_comparison_data(
			queryset, normalize('NFKD', 'Homicídio Culposo'))
		trafico = get_comparison_data(
			queryset, normalize('NFKD', 'Tráfico Ilícito de Drogas'))
		comparison = [furto, roubo, uso, homicidio_d, homicidio_c, trafico]

	mad, mat, vesp, noturno = generate_horarios(get_time(lst))
	horarios = [mad, mat, vesp, noturno]

	return [[naturezas, bairros, vias, locais,
		weekdays], comparison, horarios]

def make_graphs(months=False, weekdays=False):
	if months:
		xaxis, yaxis = get_month_axis(months)
		return months, xaxis, yaxis
	if weekdays:
		xaxis, yaxis = get_weekday_axis(weekdays)
		return weekdays, xaxis, yaxis


def calculate_variation(a, b):
	"""
	Calculates variation relative from b to a.
	a < b: percent. of Increase, if a > b: percent. of decrease
	"""
	if (b == 0):
		percentage = 0
	else:
		percentage = (abs(a - b) / b) * 100
	return percentage


def get_percentage(a, b):
	"""Gets percentage using calculate_variation(), taking into
	account which args should go where"""
	a = int(a)
	b = int(b)
	if a < b:
		return calculate_variation(a, b)
	else:
		return calculate_variation(b, a)

def get_value(queryset, field, limit):
	"""Takes a queryset, filtering it according to the field and
	limit args, returning a namedtuple, as of prepare_data()"""
	data = queryset.values(field).annotate(num=Count('id'))
	data = data.order_by('-num')[:limit]
	data = prepare_data(data, field)
	return data

def get_values(queryset, field1, field2, limit):
	data = queryset.values(field1, field2).annotate(num=Count('id'))
	data = data.order_by('-num')[:limit]
	data = prepare_double_field_data(data, field1, field2)
	return data	

def get_comparison_data(queryset, param):
	try:
		data = queryset.filter(natureza__contains=param).values(
			'natureza').annotate(num=Count('id'))[0]
	except IndexError:
		data = {'natureza': param, 'num': 0}
	return data

def get_natureza(querylst):
	"""Return a list of data sorted by natureza"""
	roubo, furto, trafico, homicidio = [], [], [], []
	for ocorrencia in querylst:
		if 'roubo' in ocorrencia.natureza.lower():
			roubo.append(ocorrencia)
		elif 'furto' in ocorrencia.natureza.lower():
			furto.append(ocorrencia)
		elif normalize('NFKD', 'tráfico de drogas') in ocorrencia.natureza.lower():
			trafico.append(ocorrencia)
		elif normalize('NFKD', 'homicídio') in ocorrencia.natureza.lower():
			homicidio.append(ocorrencia)
	return [roubo, furto, trafico, homicidio]

def prepare_data(querylst, field):
	"""Wraps the data for iteration on the template"""
	data = []
	for row in querylst:
		data.append(Response(row[field], row['num'], field))
	return data

def prepare_double_field_data(querylst, field1, field2):
	"""Wraps the data for iteration on the template"""
	data = []
	for row in querylst:
		data.append(Response(row[field1] + ', ' + row[field2], row['num'],
			field1 + ', ' + field2))
	return data

def get_time(querylst):
	"""Returns a list, with the data sorted by time blocks"""
	madrugada, matutino, vespertino, noturno = [], [], [], []
	for ocorrencia in querylst:
		if ocorrencia.hora is None:
			continue
		if time(0) <= ocorrencia.hora < time(6):
			madrugada.append(ocorrencia)
		elif time(6) <= ocorrencia.hora < time(12):
			matutino.append(ocorrencia)
		elif time(12) <= ocorrencia.hora < time(18):
			vespertino.append(ocorrencia)
		else:
			noturno.append(ocorrencia)
	return madrugada, matutino, vespertino, noturno

def generate_horarios(horarios):
	"""Takes a lst of horarios and returns a lst in the Response format"""
	lst = []
	tags = ['00:00 - 05:59', '06:00 - 11:59', '12:00 - 17:59', '18:00 - 23:59']
	for horario, tag in zip(horarios, tags):
		lst.append(Response(tag, len(horario), 'Horário'))
	return lst

def get_weekdays(queryset):
	"""Returns a list, with the number of records by weekday"""
	weekdays = []
	for i in range(1, 8):
		d = queryset.filter(data__week_day=i)
		try:
			d = Response(d[0].data, d.count(), 'Dia da semana')
		except IndexError:
			continue
		weekdays.append(d)
	return weekdays

def get_months(queryset):
	months = []
	for i in range(1, 13):
		m = queryset.filter(data__month=i)
		try:
			m = Response(m[0].data, m.count(), 'Mês')
		except IndexError:
			continue
		months.append(m)
	return months

def get_month_axis(months):
	xaxis, yaxis = [], []
	for month in months:
		xaxis.append(monthnames[month.field.month])
		yaxis.append(month.num)
	return xaxis, yaxis

def get_weekday_axis(wds):
	xaxis, yaxis = [], []
	for wd in wds:
		xaxis.append(weekdays[wd.field.weekday()][:3])
		yaxis.append(wd.num)
	return xaxis, yaxis

def get_axis(namedtpl):
	xaxis, yaxis = [], []
	for item in namedtpl:
		xaxis.append(item.field)
		yaxis.append(item.num)
	return xaxis, yaxis

