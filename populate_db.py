# Must be run from the inside of the app dir, so that
# the model can be imported

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PMMT.settings')

import django
django.setup()

import csv
from datetime import date, time
from setup_app.models import Ocorrencia

def insert_data(filename, date_format, verbose=False):
	"""
	Fetches the data from a csv file and inserts it to the DB.
	- If no date or time are available, the field must be empty.
	"""
	with open(filename, 'rt', encoding='utf-8') as fin:
		table = [row for row in csv.reader(fin)]
	
	for row in table:
		obj = Ocorrencia(
			data=resolve_date(row[1], date_format), 
			bairro=if_exists(row[2]), 
			via=if_exists(row[3]),
			numero=if_exists(row[4]), 
			natureza=if_exists(row[0]), 
			hora=resolve_time(row[5])
		)
		obj.save()
		if verbose:
			print("Ocorrência %s inserida, de %s com sucesso." % (
				row[0],row[1]))

def resolve_date(input_date, format):
	"""
	Gets a date str as input and returns a datetime.date object.
	Input date must be in dd/mm/yyyy format.
	"""
	if input_date == '':
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
	if input_time == '':
		return None
	second = 0
	try:
		hour, minute, second = input_time.split(':')
	except ValueError:
		hour, minute = input_time.split(':')
	return time(int(hour), int(minute), int(second))

def if_exists(val):
	return val if val else None


if __name__ == '__main__':
	print("Insira o arquivo para popular o BD:")
	filepath = input("> ")
	insert_data(filepath, date_format='br', verbose=True)
	print("Done")