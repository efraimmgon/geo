"""
General purpose functions from the analise_criminal module.
"""

from django.core import serializers

from datetime import date
import json
from unicodedata import normalize

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
	Returns data as JSON
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
	bairro = normalize(
		'NFKD', form_advanced.cleaned_data['bairro']
	)
	via = normalize(
		'NFKD', form_advanced.cleaned_data['via']
	)
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
	o = format_data(o) # return JSON
	return o

def normalize_strings():
	"""
	I'm still fucking it when inserting data to the DB, so I have
	to loop through the inserted data to normalize them...
	"""
	o = Ocorrencia.objects.all()

	for obj in o:
		if obj.local:
			obj.local = normalize('NFKD', obj.local)
		if obj.bairro:
			obj.bairro = normalize('NFKD', obj.bairro)
		if obj.via:
			obj.via = normalize('NFKD', obj.via)
		obj.natureza = normalize('NFKD', obj.natureza)
		obj.save()

