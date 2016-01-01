# Must be run from the inside of the app dir, so that
# the model can be imported

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
	'PMMT.settings'
)

import django
django.setup()

import csv
from datetime import date, time
from setup_app.models import Ocorrencia

def insert_data(filename):
	"""
	Fetches the data from a csv file and inserts it to the DB.
	File format: [0] natureza, [1] data, [2] endereço, [3] hora.
	- If no date or time are available, the field must be empty.
	"""
	with open(filename, 'rt', encoding='utf-8') as fin:
		cin = csv.reader(fin)
		table = [row for row in cin]

	for row in table:
		input_date = resolve_date(row[1])
		input_address = row[2]
		input_crime = row[0]
		input_time = resolve_time(row[3])

		o = Ocorrencia(
			data=input_date, local=input_address, 
			natureza=input_crime, hora=input_time
		)
		o.save()

def resolve_date(input_date):
	"""
	Gets a date str as input and returns a datetime.date object.
	Input date must be in yyyy/mm/dd format.
	"""
	if input_date == '':
		resolved_date = None
		return resolved_date

	date_lst = input_date.split('/')
	year = int(date_lst[0])
	month = int(date_lst[1])
	day = int(date_lst[2])
	
	resolved_date = date(year, month, day)
	return resolved_date

def resolve_time(input_time):
	"""
	Gets a time str as input and returns a datetime.time object.
	Input time must be in hh:mm:ss or hh:mm format.
	"""
	if input_time == '':
		resolved_time = None
		return resolved_time

	time_lst = input_time.split(':')

	hour = int(time_lst[0])
	minute = int(time_lst[1])

	if len(time_lst) == 3:
		second = int(time_lst[2])
		resolved_time = time(hour, minute, second)
	else:
		resolved_time = time(hour, minute)

	return resolved_time


if __name__ == '__main__':
	print("Insira o arquivo para popular o BD:")
	filepath = input("> ")

	insert_data(filepath)

	print("Done")