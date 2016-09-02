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
