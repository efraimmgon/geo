"""
- Functions from the report and make_report func from analise_criminal.views
"""

from django.db.models import Count

from datetime import time
from unicodedata import normalize
from collections import OrderedDict

from setup_app.models import Ocorrencia
from .collections import (
	MONTHNAMES, WEEKDAYS, WEEKDAYS_DJANGO, Response, Struct
)


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
	
	context = {}
	A = Struct()
	B = Struct()

	## context is composed of the following keys:
	# forms; dates; total; axis; basico; comparison; filtro; bairro; detalhaento
	context['forms'] = {'report': form_report, 'filter': form_filter}

	A.start = form_report.cleaned_data['data_inicial_a']
	A.end   = form_report.cleaned_data['data_final_a']
	B.start = form_report.cleaned_data['data_inicial_b']
	B.end   = form_report.cleaned_data['data_final_b']

	o1 = Ocorrencia.objects.filter(data__gte=A.start, 
								   data__lte=A.end)
	o2 = Ocorrencia.objects.filter(data__gte=B.start, 
								   data__lte=B.end)

	context['a'] = {
		'start': A.start,
		'end': A.end,
		'total': o1.count()
	}
	context['b'] = {
		'start': B.start,
		'end': B.end,
		'total': o2.count()
	}

	# GENERAL ANALYSIS + GRAPHS
	if form_report.cleaned_data['opts'] == 'Sim':
#		natures  = get_natures(o)
#		hoods 	 = get_neighborhoods(o)
#		routes 	 = get_routes(o)
#		spots 	 = get_spots(o)
#		weekdays = get_weekdays(o)
#		horaries = get_horaries(o)

		a, comparison1, horarios1 = process_args(o1, compare=True)
		naturezas1, bairros1, vias1, locais1, weekdays1 = a

		b, comparison2, horarios2 = process_args(o2, compare=True)
		naturezas2, bairros2, vias2, locais2, weekdays2 = b

		# GRAPHS
		context['axis'] = OrderedDict()
		context['axis'].update( 
			append_axis(
				tags=['naturezas', 'bairros', 'vias', 'horários'],
				data_lst=[{'a': naturezas1, 'b': naturezas2}, 
						  {'a': bairros1, 'b': bairros2},
						  {'a': vias1, 'b': vias2}, 
						  {'a': horarios1, 'b': horarios2}],
				names={'a': 'Período A', 'b': 'Período B'}
			)
		)

		wd_xaxis1, wd_yaxis1 = get_axis(weekdays1)
		wd_xaxis2, wd_yaxis2 = get_axis(weekdays2)
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


### Specialized DB parameter fetching functions; return ints

def get_natures(queryset, limit=5):
	return get_values(queryset, ['natureza'], limit=limit)

def get_neighborhoods(queryset, limit=5):
	return get_values(queryset.exclude(bairro=None), ['bairro'], limit=limit)

def get_routes(queryset, limit=5):
	return get_values(queryset.exclude(via=None), ['via'], limit=limit)

def get_spots(queryset, limit=5):
	return get_values(
		queryset.exclude(bairro=None).exclude(via=None), 
		['bairro', 'via'], limit=limit
	)

def get_weekdays(queryset):
	"""
	Takes a queryset.
	Returns a Response object, with 'field', 'num', and 'type' properties.
	"""
	return count_objs(
		queryset, delimitor=range(1, 8), type="Dia da semana",
		funcqs=lambda qs, i: qs.filter(data__week_day=i),
		## fill in the respective descriptive weekday name
		funcfield=lambda qs: WEEKDAYS[qs[0].data.weekday()])

def get_horaries(queryset):
	"""
	Takes a queryset.
	Returns a Response object, with 'field', 'num', and 'type' properties.
	"""
	TAGS = ('00:00 - 05:59', '06:00 - 11:59', '12:00 - 17:59', '18:00 - 23:59')
	return [ Response(field=tag, num=len(horary), type='Horário')
				for horary, tag in zip(get_time(list(queryset)), TAGS) ]


### Other functions

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

def prepare_data(querylst, field):
	"""Wraps the data for iteration on the template"""
	return [Response(field=row[field], num=row['num'], type=field) for row in querylst]

def prepare_double_field_data(querylst, field1, field2):
	"""Wraps the data for iteration on the template"""
	return [Response(field=row[field1]+', '+row[field2], num=row['num'], 
		type=row[field1]+', '+row[field2]) for row in querylst]


### Count occurrences of specific objects

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

def count_objs(queryset, delimitor, type, funcqs, funcfield):
	"""
	Returns a Response object, containing a field, num, and type properties.

	INPUTS
	queryset: a queryset
	delimitor: a delimiting range, serving as the iteration's index; 
	type: a type label for the Response object;
	funcqs: a function that takes the queryset and index as input;
	funcfield: a function that takes the queryset, prior to saving it in
	Response.field;
	"""
	acc = []
	for i in delimitor:
		qs = funcqs(queryset, i)
		try:
			acc.append(Response(field=funcfield(qs), num=qs.count(), type=type))
		except IndexError:
			continue
	return acc

def get_weekdays(queryset):
	"""
	Takes a queryset and counts the ocurrences of each weekday,
	using count_objs and custom functions for funcqs and funcfield.
	"""
	return count_objs(
		queryset, delimitor=range(1, 8), type="Dia da semana",
		funcqs=lambda qs, i: qs.filter(data__week_day=i),
		funcfield=lambda qs: WEEKDAYS[qs[0].data.weekday()])

def count_months(queryset):
	"""
	Takes a queryset; counts records by months and returns 
	them inside a Response namedtuple.
	"""
	return count_objs(
		queryset, delimitor=range(1, 13), type="Mês",
		funcqs=lambda qs, i: qs.filter(data__month=i),
		funcfield=lambda qs: MONTHNAMES[qs[0].data.month])
	

### Ploting functions

def get_axis(objs, funcx=lambda x: x.field, funcy=lambda y: y.num):
	"""
	Processes 'objs' inside a genexp as to get the x and y axis.
	- Takes a list of objects and two functions that will be used to
	define how the obj will be returned.
	- The functions default to return x.field and y.num.
	- Returns a tuple of lists of 'xaxis' and 'yaxis'.
	"""
	xaxis = (funcx(obj) for obj in objs)
	yaxis = (funcy(obj) for obj in objs)
	return xaxis, yaxis

def nature_per_month_axis(queryset, nats):
	"""
	Takes a queryset and a list of natures. Returns a dict of
	natures (keys) per month (x, y axis).
	"""
	context_dct = OrderedDict()
	for nat in nats:
		xaxis, yaxis = get_axis(
						count_months(
							queryset.filter(natureza__icontains=nat)))
		context_dct[nat] = {'x': xaxis, 'y': yaxis}
	return context_dct

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

def append_axis(tags, data_lst, names):
	context_dct = OrderedDict()
	for tag, data in zip(tags, data_lst):
		xaxis1, yaxis1 = get_axis(data['a'])
		xaxis2, yaxis2 = get_axis(data['b'])
		context_dct[tag] = [
			{'x': xaxis1, 'y': yaxis1, 'id': 'id_%s_graph' % tag,
			'color': 'rgb(255,0,0)', 'name': names['a']},
			{'x': xaxis2, 'y': yaxis2, 'id': 'id_%s_graph' % tag,
			'color': 'rgb(255,255,0)', 'name': names['b']},
		]
	return context_dct

