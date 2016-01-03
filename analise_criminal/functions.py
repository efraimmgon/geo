from django.core import serializers
from datetime import date
import json

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

		if ',' in obj['fields']['local']:
			lst = obj['fields']['local'].split(',')
			obj['fields']['bairro'] = lst[0]
			obj['fields']['via'] = lst[1].strip()
		else:
			obj['fields']['bairro'] = obj['fields']['local']
			obj['fields']['via'] = obj['fields']['local']
		del obj['fields']['local']
			
	return json.dumps(struct)


def add_venue_hood():
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

