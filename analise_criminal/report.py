"""
- Functions from the report and make_report func from analise_criminal.views
"""

from django.db.models import Count

from datetime import time
from unicodedata import normalize
from collections import namedtuple

from setup_app.models import Ocorrencia


def process_report_arguments(form_report, form_filter):
	"""
	Uses user's selections to decide what analysis to process,
	and what data to present.
	"""
	context = {}
	Response = namedtuple('Response', ['field', 'num', 'type'])

	context['form_report'] = form_report
	context['form_filter'] = form_filter

	data_inicial_a = form_report.cleaned_data['data_inicial_a']
	data_final_a = form_report.cleaned_data['data_final_a']
	data_inicial_b = form_report.cleaned_data['data_inicial_b']
	data_final_b = form_report.cleaned_data['data_final_b']

	data_a = data_inicial_a.strftime('%d-%m-%Y') 
	data_a += ' a ' + data_final_a.strftime('%d-%m-%Y')
	data_b = data_inicial_b.strftime('%d-%m-%Y')
	data_b += ' a ' + data_final_b.strftime('%d-%m-%Y')
	context['data'] = {
		'a': data_a,
		'b': data_b,
	}

	o1 = Ocorrencia.objects.filter(
		data__gte=data_inicial_a, data__lte=data_final_a
	)
	o2 = Ocorrencia.objects.filter(
		data__gte=data_inicial_b, data__lte=data_final_b
	)

	lst_a = list(o1)
	lst_b = list(o2)

	# A
	naturezas1 = get_value(o1, 'natureza', limit=5)
	bairros1 = get_value(o1.exclude(bairro=None), 'bairro', limit=5)
	vias1 = get_value(o1.exclude(via=None), 'via', limit=10)
	locais1 = get_values(
		o1.exclude(bairro=None).exclude(via=None), 'bairro', 'via', 5
	)
	weekdays1 = get_weekdays(o1)

	# B
	naturezas2 = get_value(o2, 'natureza', limit=5)
	bairros2 = get_value(o2.exclude(bairro=None), 'bairro', limit=5)
	vias2 = get_value(o2.exclude(via=None), 'via', limit=10)
	locais2 = get_values(
		o2.exclude(bairro=None).exclude(via=None), 'bairro', 'via', 5
	)
	weekdays2 = get_weekdays(o2)

	## Comparison A/B
	# data fluctuation of a in relation to b, and vice-versa
	# A
	furto1 = get_comparison_data(o1, 'Furto')
	roubo1 = get_comparison_data(o1, 'Roubo')
	uso1 = get_comparison_data(
		o1, normalize('NFKD', 'Uso Ilícito de Drogas'))
	homicidio_d1 = get_comparison_data(
		o1, normalize('NFKD', 'Homicídio Doloso'))
	homicidio_c1 = get_comparison_data(
		o1, normalize('NFKD', 'Homicídio Culposo'))
	trafico1 = get_comparison_data(
		 o1, normalize('NFKD', 'Tráfico Ilícito de Drogas'))

	# B
	furto2 = get_comparison_data(o2, 'Furto')
	roubo2 = get_comparison_data(o2, 'Roubo')
	uso2 = get_comparison_data(
		o2, normalize('NFKD', 'Uso Ilícito de Drogas'))
	homicidio_d2 = get_comparison_data(
		o2, normalize('NFKD', 'Homicídio Doloso'))
	homicidio_c2 = get_comparison_data(
		o2, normalize('NFKD', 'Homicídio Culposo'))
	trafico2 = get_comparison_data(
		o2, normalize('NFKD', 'Tráfico Ilícito de Drogas'))

	# Timings
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

	context['total'] = {'a': o1.count(), 'b': o2.count(), 
	'variation': percent_total}

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

	# Filter: natureza
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

	return context


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
	roubo = []
	furto = []
	trafico = []
	homicidio = []
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
	Response = namedtuple('Response', ['field', 'num', 'type'])
	data = []
	for row in querylst:
		data.append(Response(row[field], row['num'], field))
	return data

def prepare_double_field_data(querylst, field1, field2):
	"""Wraps the data for iteration on the template"""
	Response = namedtuple('Response', ['field', 'num', 'type'])
	data = []
	for row in querylst:
		data.append(Response(row[field1] + ', ' + row[field2], row['num'],
			field1 + ', ' + field2))
	return data

# unused so far...
def fetch_data(queryset, field, limit):
	"""
	1 - Returns the data filtered on the database.
	2 - Wraps the data for iteration on the template.
	"""
	data = get_value(queryset, field, limit)
	data = prepare_data(data, field)
	return data


def get_time(querylst):
	"""Returns a list, with the data sorted by time blocks"""
	madrugada = []
	matutino = []
	vespertino = []
	noturno = []
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
	return [madrugada, matutino, vespertino, noturno]

def get_weekdays(queryset):
	"""Returns a list, with the number of records by weekday"""
	Response = namedtuple('Response', ['field', 'num', 'type'])
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
	Response = namedtuple('Response', ['field', 'num', 'type'])
	months = []
	for i in range(1, 13):
		m = queryset.filter(data__month=i)
		try:
			m = Response(m[0].data, m.count(), 'Mês')
		except IndexError:
			continue
		months.append(m)
	return months