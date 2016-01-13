from django.core import serializers
from django.db.models import Count
from datetime import date, time
import json
import unicodedata

from setup_app.models import Ocorrencia

weekdays = {
		0: 'Segunda',
		1: 'Terça',
		2: 'Quarta',
		3: 'Quinta',
		4: 'Sexta',
		5: 'Sábado',
		6: 'Domingo'
	}

def format_data(objs):
	"""
	- Adds a fields with a date in the format dd/mm/yyyy;
	- Adds a weekday string; strips seconds from time
	- Splits the address and creates a fields for the neighborhood
	and street.
	"""
	

	copy = objs[:]
	data = serializers.serialize('json', copy)
	struct = json.loads(data)

	for obj in struct:
		date_lst = obj['fields']['data'].split('-')
		d = date(int(date_lst[0]), int(date_lst[1]), int(date_lst[2]))
		
		obj['fields']['formatted_date'] = d.strftime('%d/%m/%Y')
		obj['fields']['weekday'] = weekdays[ d.weekday() ]
		
		if obj['fields']['hora'] is None:
			continue
		else:
			obj['fields']['hora'] = obj['fields']['hora'][:-3]
			
	return json.dumps(struct)

def make_weekdays(objs):
	o = objs[:]
	for obj in o:
		obj.weekday = weekdays[ obj.data.weekday() ]
	return o



def add_venue_hood():
	"""Adds 'bairro' and 'via' to  an obj"""
	o = Ocorrencia.objects.values('local').distinct()

	for obj in o:
		if ',' in obj['local']:
			lst = obj['local'].split(',')
			obj['bairro'] = lst[0]
			obj['via'] = lst[1].strip()
		else:
			obj['bairro'] = obj['local']
			obj['via'] = obj['local']
		del obj['local']

	return o


def insert_bairro_and_via_db():
	"""Since I fucked up and originally created only a local
	field to locate an address, I had to create this hack to include
	a bairro, via, numero field into the existing db."""
	objs = Ocorrencia.objects.all()
	for obj in objs:
		if ',' in obj.local:
			lst = obj.local.split(',')
			obj.bairro = lst[0].strip()
			obj.via = lst[1].strip()
			if len(lst) == 3:
				obj.numero = lst[2].strip()
		else:
			obj.bairro = obj.local
			obj.via = obj.local
		obj.save()
	print('Done')


def process_map_arguments(
	natureza, data_inicial, data_final, bairro, 
	via, hora_inicial, hora_final
	):
	"""Uses the selections from the user to decide which objects
	from Ocorrencia to return"""
	if natureza == 'todas':
		o = Ocorrencia.objects.filter(
			data__gte=data_inicial, data__lte=data_final
		)
	else:
		o = Ocorrencia.objects.filter(
			natureza=natureza, data__gte=data_inicial, data__lte=data_final
		)

	if bairro:
		o = o.filter(bairro__icontains=bairro)
	if via:
		o = o.filter(via__icontains=via)
	if hora_inicial:
		o = o.filter(hora__gte=hora_inicial)
	if hora_final:
		o = o.filter(hora__lte=hora_final)

	o = o.exclude(latitude=None)

	return o

def normalize_strings():
	o = Ocorrencia.objects.all()

	for obj in o:
		if obj.local:
			obj.local = unicodedata.normalize('NFKD', obj.local)
		if obj.bairro:
			obj.bairro = unicodedata.normalize('NFKD', obj.bairro)
		if obj.via:
			obj.via = unicodedata.normalize('NFKD', obj.via)
		obj.natureza = unicodedata.normalize('NFKD', obj.natureza)
		obj.save()

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
	a = int(a)
	b = int(b)
	if a < b:
		return calculate_variation(a, b)
	else:
		return calculate_variation(b, a)

def get_value(queryset, field, limit):
	data = queryset.values(field).annotate(num=Count('id'))
	data = data.order_by('-num')[:limit]
	return data

def get_values(queryset, field1, field2, limit):
	data = queryset.values(field1, field2).annotate(num=Count('id'))
	data = data.order_by('-num')[:limit]
	return data	

def get_comparison_data(queryset, param):
	try:
		data = queryset.filter(natureza__contains=param).values(
			'natureza').annotate(num=Count('id'))[0]
	except IndexError:
		data = {'natureza': param, 'num': 0}
	return data

def get_time(querylst):
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