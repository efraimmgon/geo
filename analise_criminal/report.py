"""
- Functions from the report and make_report func from analise_criminal.views
"""

from django.db.models import Count

from datetime import time
from unicodedata import normalize
from collections import namedtuple

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
	"""Gets percentage using calculate_variation(), taking into
	account which args should go where"""
	a = int(a)
	b = int(b)
	if a < b:
		return calculate_variation(a, b)
	else:
		return calculate_variation(b, a)

def get_value(queryset, field, limit):
	"""Takes a queryset, filtering it according to the field and
	limit args, returning a namedtuple, as of prepare_data()"""
	data = queryset.values(field).annotate(num=Count('id'))
	data = data.order_by('-num')[:limit]
	data = prepare_data(data, field)
	return data

def get_values(queryset, field1, field2, limit):
	data = queryset.values(field1, field2).annotate(num=Count('id'))
	data = data.order_by('-num')[:limit]
	data = prepare_double_field_data(data, field1, field2)
	return data	

def get_comparison_data(queryset, param):
	try:
		data = queryset.filter(natureza__contains=param).values(
			'natureza').annotate(num=Count('id'))[0]
	except IndexError:
		data = {'natureza': param, 'num': 0}
	return data

def get_natureza(querylst):
	"""Return a list of data sorted by natureza"""
	roubo = []
	furto = []
	trafico = []
	homicidio = []
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
	Response = namedtuple('Response', ['field', 'num', 'type'])
	data = []
	for row in querylst:
		data.append(Response(row[field], row['num'], field))
	return data

def prepare_double_field_data(querylst, field1, field2):
	"""Wraps the data for iteration on the template"""
	Response = namedtuple('Response', ['field', 'num', 'type'])
	data = []
	for row in querylst:
		data.append(Response(row[field1] + ', ' + row[field2], row['num'],
			field1 + ', ' + field2))
	return data

# unused so far...
def fetch_data(queryset, field, limit):
	"""
	1 - Returns the data filtered on the database.
	2 - Wraps the data for iteration on the template.
	"""
	data = get_value(queryset, field, limit)
	data = prepare_data(data, field)
	return data


def get_time(querylst):
	"""Returns a list, with the data sorted by time blocks"""
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