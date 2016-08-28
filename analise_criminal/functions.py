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
from .utils import WEEKDAYS, Struct


def make_weekdays(objs):
	o = objs[:]
	for obj in o:
		obj.weekday = WEEKDAYS[ obj.data.weekday() ]
	return o

def process_map_arguments(form, form_advanced):
	"""
	Uses the user's selections to decide which objects
	from Ocorrencia to return.
	"""
	natureza = form.cleaned_data['natureza']
	data_inicial = form.cleaned_data['data_inicial']
	data_final = form.cleaned_data['data_final']
	hora_inicial = form_advanced.cleaned_data['hora_inicial']
	hora_final = form_advanced.cleaned_data['hora_final']
	bairro = normalize('NFKD', form_advanced.cleaned_data['bairro'])
	via = normalize('NFKD', form_advanced.cleaned_data['via'])

	if natureza == 'todas':
		qs = Ocorrencia.objects.filter(
			data__gte=data_inicial, data__lte=data_final)
	else:
		qs = Ocorrencia.objects.filter(
			natureza__icontains=natureza, data__gte=data_inicial, data__lte=data_final)

	if bairro:
		qs = qs.filter(bairro__icontains=bairro)
	if via:
		qs = qs.filter(via__icontains=via)
	if hora_inicial:
		qs = qs.filter(hora__gte=hora_inicial)
	if hora_final:
		qs = qs.filter(hora__lte=hora_final)

	## prepare data for returning
	return format_data(qs.exclude(latitude=None).exclude(latitude=0.0))

def format_data(queryset):
	"""
	- Adds a fields with a date in the format dd/mm/yyyy;
	- Adds a weekday string; strips seconds from time
	- Splits the address and creates a fields for the neighborhood
	and street.
	Returns a list of dicts.
	"""
	struct = []
	for obj in queryset:
		dct = {
			'pk': obj.id,
			'natureza': obj.natureza,
			'bairro': obj.bairro,
			'via': obj.via,
			'numero': obj.numero,
			'formatted_date': obj.date2string(),
			'weekday': obj.weekday(),
			'hora': str(obj.hora)[:-3] if obj.hora else None,
			'latitude': obj.latitude,
			'longitude': obj.longitude
		}
		struct.append(dct)
	return struct


### GRAPHS

def make_graph(func, queryset, fields, plot, title, color=''):
	"""
	Takes several args required to make a Plotly graph, plus a function,
	which will do the work of generating the fields required.
	Returns a Graph object.
	"""
	field, occurrences = func(
		queryset.values(fields[0]).annotate(num=Count('id')), fields[0])
	return Struct(x=field, y=occurrences, plot_type=plot,
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
