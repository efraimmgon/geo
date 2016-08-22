import csv
from datetime import date, time
from setup_app.models import Ocorrencia
from django.db import transaction


def populate_db(csv_data, city, date_format, verbose=False):
	"""
	Inserts csv data into the DB.
	`csv_data` is list representing that.
	- The fields must be in the following index order:
		0) incident; 1) neighborhood; 2) venue; 3) number; 4) time;
		5) date
	- If no date or time are available, the fields must be empty.
	- date must be in dd/mm/yyyy format
	"""
	result = []
	with transaction.atomic():
		for row in csv_data:
			obj = Ocorrencia(
				natureza=val_or_none(row[0]), 
				bairro= val_or_none(row[1]), 
				via=	val_or_none(row[2]),
				numero= val_or_none(row[3]), 
				hora=	resolve_time(row[4]),
				data=	resolve_date(row[5], date_format), 
				cidade=	city,
			)
			obj.save()
			if verbose:
				result.append("Ocorrência %s de %s inserida com sucesso." % (
					row[0], row[1]))
	return result

def resolve_date(input_date, format):
	"""
	Gets a date str as input and returns a datetime.date object.
	Input date must be in dd/mm/yyyy format.
	"""
	if input_date == '' or input_date == 'NI':
		return None
	if format == 'br':
		day, month, year = input_date.split('/')
	elif format == 'us':
		year, month, day = input_date.split('/')
	return date(int(year), int(month), int(day))

def resolve_time(input_time):
	"""
	Gets a time str as input and returns a datetime.time object.
	"""
	if input_time == '' or input_time == 'NI':
		return None
	second = 0
	try:
		hour, minute, second = input_time.split(':')
	except ValueError:
		hour, minute = input_time.split(':')
	return time(int(hour), int(minute), int(second))

def val_or_none(val):
	if val.lower() in UNKNOWN:
		return None
	return val.title()

UNKNOWN = [
	"", "ni", "não informado", "nao informado", "nao especificado",
	"não especificado", "outro", "outros",
]