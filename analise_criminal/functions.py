"""
General purpose functions from the analise_criminal module.
"""

from django.core import serializers
from django.db.models import Count

from datetime import date
import json
from unicodedata import normalize
from collections import OrderedDict

from setup_app.models import Ocorrencia
from .collections import WEEKDAYS, Response, Graph
from .report import get_values


def format_data(objs):
	"""
	- Adds a fields with a date in the format dd/mm/yyyy;
	- Adds a weekday string; strips seconds from time
	- Splits the address and creates a fields for the neighborhood
	and street.
	Returns data as JSON
	"""
	data = serializers.serialize('json', objs[:])
	struct = json.loads(data)

	for obj in struct:
		date_lst = obj['fields']['data'].split('-')
		d = date(int(date_lst[0]), int(date_lst[1]), int(date_lst[2]))
		
		obj['fields']['formatted_date'] = d.strftime('%d/%m/%Y')
		obj['fields']['weekday'] = WEEKDAYS[ d.weekday() ]
		
		if obj['fields']['hora'] is None:
			continue
		else:
			obj['fields']['hora'] = obj['fields']['hora'][:-3]
			
	return json.dumps(struct)

def make_weekdays(objs):
	o = objs[:]
	for obj in o:
		obj.weekday = WEEKDAYS[ obj.data.weekday() ]
	return o

def process_map_arguments(form, form_advanced):
	"""Uses the selections from the user to decide which objects
	from Ocorrencia to return"""
	natureza = normalize(
			'NFKD', form.cleaned_data['natureza']
	)
	data_inicial = form.cleaned_data['data_inicial']
	data_final = form.cleaned_data['data_final']
	hora_inicial = form_advanced.cleaned_data['hora_inicial']
	hora_final = form_advanced.cleaned_data['hora_final']
	bairro = normalize('NFKD', form_advanced.cleaned_data['bairro'])
	via = normalize('NFKD', form_advanced.cleaned_data['via'])
	if natureza == 'todas':
		o = Ocorrencia.objects.filter(
			data__gte=data_inicial, data__lte=data_final)
	else:
		o = Ocorrencia.objects.filter(
			natureza__icontains=natureza, data__gte=data_inicial, data__lte=data_final)

	if bairro:
		o = o.filter(bairro__icontains=bairro)
	if via:
		o = o.filter(via__icontains=via)
	if hora_inicial:
		o = o.filter(hora__gte=hora_inicial)
	if hora_final:
		o = o.filter(hora__lte=hora_final)

	o = o.exclude(latitude=None).exclude(latitude=0.0)
	o = format_data(o) # return JSON
	return o

def normalize_strings():
	"""
	I'm still fucking it when inserting data to the DB, so I have
	to loop through the inserted data to normalize them...
	"""
	queryset = Ocorrencia.objects.all()

	for obj in queryset:
		if obj.local:
			obj.local = normalize('NFKD', obj.local)
		if obj.bairro:
			obj.bairro = normalize('NFKD', obj.bairro)
		if obj.via:
			obj.via = normalize('NFKD', obj.via)
		obj.natureza = normalize('NFKD', obj.natureza)
		obj.save()

def make_graph(func, queryset, fields, plot, title, color=''):
	"""
	Takes several args required to make a Plotly graph, plus a function,
	which will do the work of generating the fields required.
	Returns a Graph object.
	"""
	field, occurrences = func(
		queryset.values(fields[0]).annotate(num=Count('id')), fields[0])
	return Graph(x=field, y=occurrences, plot_type=plot,
		title=title, color=color)

def make_days_graph(queryset, plot, title, color=''):
	"""
	Returnes a Graph object with the necessary properties 
	to make a Plotly graph with days.
	"""
	return make_graph(func=fetch_graph_data, queryset=queryset,
		fields=['data'], plot=plot, title=title, color=color)

def make_neighborhood_graph(queryset, plot, title, color=''):
	"""
	Returnes a Graph object with the necessary properties 
	to make a Plotly graph with days.
	"""
	return make_graph(func=fetch_graph_data, queryset=queryset,
		fields=['bairro'], plot=plot, title=title, color=color)

def make_street_graph(queryset, plot, title, color=''):
	"""
	Returnes a Graph object with the necessary properties 
	to make a Plotly graph with days.
	"""
	return make_graph(func=fetch_graph_data, queryset=queryset,
		fields=['via'], plot=plot, title=title, color=color)

def make_nature_graph(queryset, plot, title, color=''):
	"""
	Returnes a Graph object with the necessary properties 
	to make a Plotly graph with days.
	"""
	return make_graph(func=fetch_graph_data, queryset=queryset,
		fields=['natureza'], plot=plot, title=title, color=color)

def make_hours_graph(queryset, plot, title, color=''):
	"""
	Returnes a Graph object with the necessary properties 
	to make a Plotly graph with hours.
	"""
	return make_graph(func=fetch_graph_hour, queryset=queryset,
		fields=['hora'], plot=plot, title=title, color=color)

def fetch_graph_data(objs, fields):
	"Returns two lists"
	field = [str(obj.get(fields)) for obj in objs]
	occurrences = [obj.get('num') for obj in objs]
	return field, occurrences

def fetch_graph_hour(objs, fields):
	"Fetchs occurrences per hour."
	# It's slightly more complicated than the others, because the hour fields
	# are duplicated, since they can have happened in different minutes inside
	# the hours. Hence, we have to loop through the qs, accumulating the occur-
	# rences per hour before we can loop again, generating the final list of
	# fields and occurrences.
	container = OrderedDict()
	for obj in objs:
		if not obj.get(fields):
			continue
		key = obj.get(fields).hour
		val = obj.get('num')
		if container.get(key):
			container[key] += val
		else:
			container[key] = val
	field = [hora for hora in container.keys()]
	occurrences = [val for val in container.values()]
	return field, occurrences



