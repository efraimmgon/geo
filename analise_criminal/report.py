"""
- Functions from the report and make_report func from analise_criminal.views
"""

from django.db.models import Count

from datetime import time
from unicodedata import normalize
from collections import OrderedDict

from setup_app.models import Ocorrencia
from .collections import MONTHNAMES, WEEKDAYS, WEEKDAYS_DJANGO, Response


NATS = ('furto', 'roubo', 'uso ilícito de drogas', 'homicídio', 
	'tráfico ilícito de drogas')
FURTO, ROUBO, USO, HOM, TRAFICO = [normalize('NFKD', nat) for nat in NATS]
NATUREZAS = (FURTO, ROUBO, USO, HOM, TRAFICO)

def process_report_arguments(form_report, form_filter):
	"""
	Uses user's selections to decide what analysis to process,
	and what data to present.
	"""
	TAGS = {
		'natures': '5 naturezas com maior registro',
		'records': '5 ocorrências com maior registro',
		'neighborhoods': '5 bairros com maior registro',
		'roads': '5 vias com maior registro',
		'places': '5 locais com maior registro',
		'weekdays': 'Registros por dia da semana',
		'time': 'Registros por horário'
	}
	## context is composed of the following keys:
	# forms; dates; total; axis; basico; comparison; filtro; bairro; detalhaento
	context = {}
	context['forms'] = {'report': form_report, 'filter': form_filter}

	data_inicial_a = form_report.cleaned_data['data_inicial_a']
	data_final_a   = form_report.cleaned_data['data_final_a']
	data_inicial_b = form_report.cleaned_data['data_inicial_b']
	data_final_b   = form_report.cleaned_data['data_final_b']

	o1 = Ocorrencia.objects.filter(data__gte=data_inicial_a, 
		data__lte=data_final_a)
	o2 = Ocorrencia.objects.filter(data__gte=data_inicial_b, 
		data__lte=data_final_b)

	context['a'] = {
		'start': data_inicial_a,
		'end': data_final_a,
		'total': o1.count()
	}
	context['b'] = {
		'start': data_inicial_b,
		'end': data_final_b,
		'total': o2.count()
	}

	# GENERAL ANALYSIS + GRAPHS
	if form_report.cleaned_data['opts'] == 'Sim':
		a, comparison1, horarios1 = process_args(o1, compare=True)
		naturezas1, bairros1, vias1, locais1, weekdays1 = a
		months1 = get_months(o1)
		xaxis1 = [MONTHNAMES[m.field.month] for m in months1]
		yaxis1 = [m.num for m in months1]

		b, comparison2, horarios2 = process_args(o2, compare=True)
		naturezas2, bairros2, vias2, locais2, weekdays2 = b
		months2 = get_months(o2)
		xaxis2 = [MONTHNAMES[m.field.month] for m in months2]
		yaxis2 = [m.num for m in months2]

		# GRAPHS
		context['axis'] = OrderedDict()
		if len(months1) > 2 or len(months2) > 2:
			context['axis']['total'] = [
				{'x': xaxis1, 'y': yaxis1, 'id': 'id_total_graph_a',
				'color': 'rgb(255,0,0)', 'name': 'Período A'},
				{'x': xaxis2, 'y': yaxis2, 'id': 'id_total_graph_a',
				'color': 'rgb(255,255,0)', 'name': 'Período B'}
			]
		append_axis(
			tags=['naturezas', 'bairros', 'vias', 'horários'],
			data_lst=[(naturezas1, naturezas2), (bairros1, bairros2),
				(vias1, vias2), (horarios1, horarios2)],
			names=['Período A', 'Período B'],
			context=context
		)

		wd_xaxis1, wd_yaxis1 = get_weekday_axis(weekdays1)
		wd_xaxis2, wd_yaxis2 = get_weekday_axis(weekdays2)
		context['axis']['Dias da semana'] = [
			{'x': wd_xaxis1, 'y': wd_yaxis1, 'id': 'id_weekday_graph_a',
			'color': 'rgb(255,0,0)', 'name': 'Período A'},
			{'x': wd_xaxis2, 'y': wd_yaxis2, 'id': 'id_weekday_graph_a',
			'color': 'rgb(255,255,0)', 'name': 'Período B'},
		]

		context['axis']['pie'] = []
		for queryset, id_ in zip([o1, o2], ['pie_a', 'pie_b']):
			labels, values = return_naturezas_axis(queryset)
			context['axis']['pie'].append(
				{'labels': labels, 'values': values, 'id': id_})

		# Percentage fluctuation from A to B
		context['comparison'] = []
		for a, b in zip(
			(get_comparison_data(o1, nat) for nat in NATUREZAS),
			(get_comparison_data(o2, nat) for nat in NATUREZAS)):
			context['comparison'].append({
				'a': a, 'b': b, 'variation': get_percentage(a['num'], b['num'])
			})
		context['variation'] = get_percentage(o1.count(), o2.count())

		context['basico'] = [
			{TAGS['records']: [naturezas1, naturezas2]},
			{TAGS['neighborhoods']: [bairros1, bairros2]},
			{TAGS['roads']: [vias1, vias2]},
			{TAGS['places']: [locais1, locais2]},
			{TAGS['weekdays']: [weekdays1, weekdays2]},
			{TAGS['time']: [horarios1, horarios2]},
		]

	if form_filter.cleaned_data['naturezas']:
		context['filtro'] = {}
		for natureza in form_filter.cleaned_data['naturezas']:
			natureza = normalize('NFKD', natureza)
			context['filtro'][natureza] = [
				{TAGS['neighborhoods']: []},
				{TAGS['roads']: []},
				{TAGS['places']: []},
				{TAGS['weekdays']: []},
				{TAGS['time']: []}
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
			{TAGS['records']: [naturezas1, naturezas2]},
			{TAGS['roads']: [vias1, vias2]},
			{TAGS['weekdays']: [weekdays1, weekdays2]},
			{TAGS['time']: [horarios1, horarios2]},
		]
	if form_filter.cleaned_data['details']:
		context['detalhamento'] = OrderedDict()
		if 'weekdays' in form_filter.cleaned_data['details']:
			weekday_detail = OrderedDict()
			for i in range(1, 8):
				weekday_detail[WEEKDAYS_DJANGO[i]] = [
					{TAGS['natures']: []},
					{TAGS['neighborhoods']: []},
					{TAGS['roads']: []},
					{TAGS['places']: []},
					{TAGS['time']: []}
				]
				current = weekday_detail[WEEKDAYS_DJANGO[i]]
				for periodo in [o1, o2]:
					(naturezas, bairros, vias, locais, _), _, horarios = process_args(
						periodo.filter(data__week_day=i), compare=False)
					values = [naturezas, bairros, vias, locais, horarios]
					for j in range(len(current)):
						for key in current[j].keys():
							current[j][key] += [values[j]]
			context['detalhamento']['semana'] = weekday_detail
		if 'time' in form_filter.cleaned_data['details']:
			time_detail = OrderedDict()
			for hora in ['00:00 - 05:59', '06:00 - 11:59', 
			'12:00 - 17:59', '18:00 - 23:59']:
				time_detail[hora] = [
					{TAGS['natures']: []},
					{TAGS['neighborhoods']: []},
					{TAGS['roads']: []},
					{TAGS['places']: []},
					{TAGS['weekdays']: []}
				]
				current = time_detail[hora]
				for periodo in [o1, o2]:
					hora_lst = hora.split(' - ')
					queryset = periodo.filter(hora__gte=hora_lst[0], hora__lte=hora_lst[1])
					(naturezas, bairros, vias, locais, wd), _, _ = process_args(
						queryset, compare=False)
					values = [naturezas, bairros, vias, locais, wd]
					for j in range(len(current)):
						for key in current[j].keys():
							current[j][key] += [values[j]]
			context['detalhamento']['horários'] = time_detail

	return context


def process_args(queryset, compare=False):
	"""
	Takes a queryset and an optional compare arg; returns generated data.
	Generates data with the given queryset; if compare is true, also
	generates comparison data.
	"""
	naturezas = get_values(queryset, ['natureza'], limit=5)
	bairros = get_values(queryset.exclude(bairro=None), ['bairro'], limit=5)
	vias = get_values(queryset.exclude(via=None), ['via'], limit=5)
	locais = get_values(
		queryset.exclude(bairro=None).exclude(via=None), ['bairro', 'via'], 5)
	weekdays = get_weekdays(queryset)

	# data fluctuation of a in relation to b, and vice-versa
	comparison = []
	if compare:
		comparison = (get_comparison_data(queryset, nat) for nat in NATUREZAS)

	TAGS = ('00:00 - 05:59', '06:00 - 11:59', '12:00 - 17:59', '18:00 - 23:59')
	periods = [Response(field=tag, num=len(horario), type='Horário') 
	for horario, tag in zip(get_time(list(queryset)), TAGS)]

	return ((naturezas, bairros, vias, locais, weekdays), comparison, periods)

def calculate_variation(a, b):
	"""
	Calculates variation relative from b to a.
	a < b: percent. of Increase, if a > b: percent. of decrease
	"""
	if (b == 0):
		return 0
	return (abs(a - b) / b) * 100


def get_percentage(a, b):
	"""
	Gets percentage using calculate_variation(), taking into
	account which args should go where.
	"""
	a, b = int(a), int(b)
	if a < b:
		return calculate_variation(a, b)
	return calculate_variation(b, a)

def get_values(queryset, fields, limit=5):
	"""
	Takes a queryset, filtering it according to the field and
	limit args, returning a namedtuple, as of prepare_data().
	"""
	if len(fields) == 2:
		data = queryset.values(fields[0], fields[1]).annotate(num=Count('id'))
		return prepare_double_field_data(data.order_by('-num')[:limit], 
			fields[0], fields[1])
	data = queryset.values(fields[0]).annotate(num=Count('id'))
	return prepare_data(data.order_by('-num')[:limit], fields[0])

def get_comparison_data(queryset, param):
	try:
		data = queryset.filter(natureza__icontains=param).values(
			'natureza').annotate(num=Count('id'))
		acc = [row['num'] for row in data]
		return {'natureza': param, 'num': sum(acc)}
	except IndexError:
		return {'natureza': param, 'num': 0}

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
	return [Response(field=row[field], num=row['num'], type=field) for row in querylst]

def prepare_double_field_data(querylst, field1, field2):
	"""Wraps the data for iteration on the template"""
	return [Response(field=row[field1]+', '+row[field2], num=row['num'], 
		type=row[field1]+', '+row[field2]) for row in querylst]

def get_time(querylst):
	"""
	Takes a querylist and use datetime.time to sort it out
	by time periods, which are then returned.
	"""
	madrugada, matutino, vespertino, noturno = [], [], [], []
	for ocorrencia in querylst:
		if ocorrencia.hora is None:
			continue
		if ocorrencia.hora < time(6):
			madrugada.append(ocorrencia)
		elif ocorrencia.hora < time(12):
			matutino.append(ocorrencia)
		elif ocorrencia.hora < time(18):
			vespertino.append(ocorrencia)
		else:
			noturno.append(ocorrencia)
	return madrugada, matutino, vespertino, noturno

def get_weekdays(queryset):
	"""
	Takes a queryset; counts records by weekday and returns 
	them inside a Response namedtuple.
	"""
	weekdays = []
	for i in range(1, 8):
		w = queryset.filter(data__week_day=i)
		try:
			w = Response(field=w[0].data, num=w.count(), type='Dia da semana')
		except IndexError:
			continue
		weekdays.append(w)
	return weekdays

def get_months(queryset):
	months = []
	for i in range(1, 13):
		m = queryset.filter(data__month=i)
		try:
			m = Response(field=m[0].data, num=m.count(), type='Mês')
		except IndexError:
			continue
		months.append(m)
	return months


### Ploting functions

def get_axis(objs, funcx=lambda x: x.field, funcy=lambda y: y.num):
	"""
	Takes a list of objects and two functions that will be used to
	define how the obj will be returned.
	Returns a tuple containing lists with an xaxis, and yaxis.
	"""
	xaxis = [funcx(obj) for obj in objs]
	yaxis = [funcy(obj) for obj in objs]
	return xaxis, yaxis

def get_month_axis(months):
	"Uses get_axis with a custom funcx to return the months axis."
	return get_axis(months, funcx=lambda x: MONTHNAMES[x.field.month])

def get_weekday_axis(wds):
	"Uses get_axis with a custom funcx to return the weekdays axis."
	return get_axis(wds, funcx=lambda x: WEEKDAYS[x.field.weekday()][:3])

def append_axis(tags, data_lst, names, context):
	for tag, data in zip(tags, data_lst):
		xaxis1, yaxis1 = get_axis(data[0])
		xaxis2, yaxis2 = get_axis(data[1])
		context['axis'][tag] = [
			{'x': xaxis1, 'y': yaxis1, 'id': 'id_%s_graph' % tag,
			'color': 'rgb(255,0,0)', 'name': names[0]},
			{'x': xaxis2, 'y': yaxis2, 'id': 'id_%s_graph' % tag,
			'color': 'rgb(255,255,0)', 'name': names[1]},
		]

def return_months_axis(queryset, filters, context):
	for f in filters:
		qs = queryset.filter(natureza__icontains=f)
		months = get_months(qs)
		xaxis, yaxis = get_month_axis(months)
		context['axis'][f] = {'x': xaxis, 'y': yaxis}
	return context

def return_naturezas_axis(queryset):
	"""
	Takes a queryset and filters it for each item in NATUREZAS.
	Returns the natures capitalized, along with a list of their counts.
	"""
	labels, values = [], []
	for nat in NATUREZAS:	
		qs = queryset.filter(natureza__icontains=nat)
		labels.append(nat.capitalize())
		values.append(qs.count())
	return labels, values

