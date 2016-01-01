from django.core import serializers
from datetime import date
import json

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
	"""Adds a fields with a date in the format dd/mm/yyyy;
	Adds a weekday string; strips seconds from time"""

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

		obj['fields']['hora'] = obj['fields']['hora'][:-3]
	
	return json.dumps(struct)