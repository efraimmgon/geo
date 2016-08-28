from django.db.models import Count

from datetime import time
from unicodedata import normalize
from collections import OrderedDict
from functools import reduce

from setup_app.models import Ocorrencia, Natureza
from .utils import (
	MONTHNAMES, WEEKDAYS, WEEKDAYS_DJANGO, Struct,
	update, lmap
)

## furto, roubo, uso, homicídio, tráfico; excluding associação
nats = [
 (3, 'Furto'),
 (4, 'Homicídio Culposo'),
 (5, 'Homicídio Doloso'),
 (6, 'Roubo'),
 (7, 'Tráfico Ilícito de Drogas'),
 (8, 'Uso Ilícito de Drogas')
]

NATUREZAS = lmap(lambda n: Natureza.objects.get(pk=n[0]), nats)
NATUREZAS_ID = reduce(lambda acc, n: update(acc, {n.pk: n.nome}),
					  NATUREZAS, {})
NATUREZAS_ID_ALL = reduce(lambda acc, n: update(acc, {n.pk: n.nome}),
					   Natureza.objects.all(), {})


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

	city = form_filter.cleaned_data['cidade']

	o1 = Ocorrencia.objects.select_related('cidade').filter(
		data__gte=A.start, data__lte=A.end, cidade=city)
	o2 = Ocorrencia.objects.select_related('cidade').filter(
		data__gte=B.start, data__lte=B.end, cidade=city)

	total_a, total_b = o1.count(), o2.count()

	context['a'] = {
		'start': A.start,
		'end': A.end,
		'total': total_a
	}
	context['b'] = {
		'start': B.start,
		'end': B.end,
		'total': total_b
	}

	# GENERAL ANALYSIS + GRAPHS
	if form_report.cleaned_data['opts'] == 'Sim':
		a, comparison1, horarios1 = process_args(o1, compare=True)
		naturezas1, bairros1, vias1, locais1, weekdays1 = a

		b, comparison2, horarios2 = process_args(o2, compare=True)
		naturezas2, bairros2, vias2, locais2, weekdays2 = b

		# GRAPHS
		context['axis'] = OrderedDict()
		context['axis'].update(
			append_axis(
				data_lst=[{'tag': 'naturezas', 'a': naturezas1, 'b': naturezas2},
						  {'tag': 'bairros', 'a': bairros1, 'b': bairros2},
						  {'tag': 'vias', 'a': vias1, 'b': vias2},
						  {'tag': 'horários', 'a': horarios1, 'b': horarios2}],
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


		def map_helper(qs, id):
			labels, values = return_naturezas_axis(qs)
			return {'labels': labels, 'values': values, 'id': id}

		context['axis']['pie'] = lmap(map_helper,
									[o1, o2], ['pie_a', 'pie_b'])

		# Percentage fluctuation from A to B
		context['comparison'] = lmap(lambda a, b: \
			{'a': a, 'b': b, 'variation': get_percentage(a['num'], b['num'])},
			comparison1, comparison2)

		context['variation'] = get_percentage(total_a, total_b)

		context['basico'] = [
			{TAGS['records']: [naturezas1, naturezas2]},
			{TAGS['neighborhoods']: [bairros1, bairros2]},
			{TAGS['roads']: [vias1, vias2]},
			{TAGS['places']: [locais1, locais2]},
			{TAGS['weekdays']: [weekdays1, weekdays2]},
			{TAGS['time']: [horarios1, horarios2]},
		]
	# End of General Analysis + Graphs

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
			for registros in [o1.filter(naturezas__nome__icontains=natureza),
							  o2.filter(naturezas__nome__icontains=natureza)]:
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


def process_args(qs, compare=False):
	"""
	Takes a qs and an optional compare arg; returns generated data.
	Generates data with the given qs; if compare is true, also
	generates comparison data.
	"""
	qs_for_naturezas = qs.select_related('cidade', 'naturezas')
	naturezas = get_qslist(qs_for_naturezas, 'naturezas')
	qs_for_bairros = qs.exclude(bairro=None).select_related('cidade')
	bairros = get_qslist(qs_for_bairros, 'bairro')
	qs_for_vias = qs.exclude(via=None).select_related('cidade')
	vias = get_qslist(qs_for_vias, 'via')
	qs_for_local = qs.exclude(bairro=None).exclude(via=None)
	locais = get_qslist(qs_for_local, 'bairro', 'via')
	weekdays = get_weekdays(qs)

	# data fluctuation of a in relation to b, and vice-versa
	comparison = []
	if compare:
		comparison = lmap(lambda n: get_comparison_data(qs, n),
						 NATUREZAS)

	TAGS = ('00:00 - 05:59', '06:00 - 11:59', '12:00 - 17:59', '18:00 - 23:59')
	## TODO: create a field `periodos` in the `Ocorrencia` model
	periods = [
		{'field':tag, 'num':len(horario), 'type':'Horário'}
		for horario, tag in zip(get_time(list(qs)), TAGS)]
#	periods = [
#		Response(field=tag, num=len(horario), type='Horário')
#		for horario, tag in zip(get_time(list(qs)), TAGS) ]

	return [(naturezas, bairros, vias, locais, weekdays), comparison, periods]


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
	Returns a dict, with 'field', 'num', and 'type' keys.
	"""
	return count_objs(
		queryset, delimitor=range(1, 8), type="Dia da semana",
		funcqs=lambda qs, i: qs.filter(data__week_day=i),
		## fill in the respective descriptive weekday name
		funcfield=lambda qs: WEEKDAYS[qs[0].data.weekday()])

def get_horaries(queryset):
	"""
	Takes a queryset.
	Returns a dict, with 'field', 'num', and 'type' keys.
	"""
	TAGS = ('00:00 - 05:59', '06:00 - 11:59', '12:00 - 17:59', '18:00 - 23:59')
	return [ dict(field=tag, num=len(horary), type='Horário')
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

def get_qslist(qs, *fields, limit=5):
	qs = qs.select_related("cidade").values(*fields).annotate(num=Count("id"))
	## pass only as many as specified in `limit`
	qs = qs.order_by('-num')[:limit]
	## pass only the pre-selected naturezas
	#if 'naturezas' in fields:
	#	qs = filter(lambda row: row["naturezas"] in NATUREZAS_ID.keys(), qs)

	def helper(field, row):
		## returns the pk of naturezas, so we need to map it to its name
		if field == 'naturezas':
			return NATUREZAS_ID_ALL.get(row.get(field))
		return row.get(field)

	return lmap(lambda row: {
		#"field": " | ".join(fields),
		"field": ", ".join(lmap(lambda f: helper(f, row), fields)),
		"num": row.get("num"),
		"type": " & ".join(fields)
		},
		## returns a list of dicts with the keys `id` and the ones on `fields`
		qs)

def get_comparison_data(queryset, param):
	try:
		data = queryset.filter(naturezas=param).values(
			'naturezas').annotate(num=Count('id'))
		acc = lmap(lambda row: row['num'], data)
		return {'natureza': param, 'num': sum(acc)}
	except IndexError:
		return {'natureza': param, 'num': 0}


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
	Returns a dict, containing a field, num, and type keys.

	INPUTS
	queryset: a queryset
	delimitor: a delimiting range, serving as the iteration's index;
	type: a type label for the dict response;
	funcqs: a function that takes the queryset and index as input;
	funcfield: a function that takes the queryset, prior to saving it in
	field;
	"""
	acc = []
	for i in delimitor:
		qs = funcqs(queryset, i)
		try:
			acc.append(dict(field=funcfield(qs), num=qs.count(), type=type))
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
	them inside a dict.
	"""
	return count_objs(
		queryset, delimitor=range(1, 13), type="Mês",
		funcqs=lambda qs, i: qs.filter(data__month=i),
		funcfield=lambda qs: MONTHNAMES[qs[0].data.month])


### Ploting functions

def get_axis(
	objs, fn_x=lambda x: x.get('field'), fn_y=lambda y: y.get('num')):
	"""
	Processes 'objs' inside a genexp as to get the x and y axis.
	- Takes a list of objects and two functions that will be used to
	define how the obj will be returned.
	- The functions default to return x.field and y.num.
	- Returns a tuple of lists of 'xaxis' and 'yaxis'.
	"""
	xaxis = lmap(fn_x, objs)
	yaxis = lmap(fn_y, objs)
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
							queryset.filter(naturezas=nat)))
		context_dct[nat] = {'x': xaxis, 'y': yaxis}
	return context_dct


def return_naturezas_axis(qs):
	"""
	Takes a queryset and filters it for each item in NATUREZAS.
	Returns the natures capitalized, along with a list of their counts.
	"""
	labels = lmap(lambda n: n.nome, NATUREZAS)
	values = lmap(lambda n: qs.filter(naturezas=n).count(),
				 NATUREZAS)
	return labels, values


def append_axis(data_lst, names):
	"""
	`data_list` is a dict of keys `tag`, `a` data and `b` data
	`names` is a dict of keys `a` tag and `b` tag
	"""
	context_dct = OrderedDict()
	for data in data_lst:
		tag = data['tag']
		xaxis1, yaxis1 = get_axis(data['a'])
		xaxis2, yaxis2 = get_axis(data['b'])
		context_dct[tag] = [
			{'x': xaxis1, 'y': yaxis1, 'id': 'id_%s_graph' % tag,
			'color': 'rgb(255,0,0)', 'name': names['a']},
			{'x': xaxis2, 'y': yaxis2, 'id': 'id_%s_graph' % tag,
			'color': 'rgb(255,255,0)', 'name': names['b']},
		]
	return context_dct
