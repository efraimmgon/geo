from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from django import forms

import json, csv
from io import StringIO

from setup_app.models import Ocorrencia, Cidade, Natureza
from setup_app.functions import dump_object
from setup_app.utils import populate_db


def index(request):
	context = {'num_rows': Ocorrencia.objects.count()}
	return render(request, 'setup_app/index.html', context)


def ajaxTest(request):
	queryset = Ocorrencia.objects.filter(latitude=0.0)[:20]
	if queryset.count() > 0:
		data = serializers.serialize('json', queryset)
	else:
		data = json.dumps({'end': 'Não existem mais lat e lng nulos.'})
	return HttpResponse(data, content_type='application/json')


def insert_records(request):
	context = {}
	form = RecordsFileForm()
	if request.method == 'POST':
		form = RecordsFileForm(request.POST, request.FILES)
		if form.is_valid():
			# TODO: normalize data before insertion #
			result = populate_db(
				read_csv_file(request.FILES["arquivo"]),
				Cidade.objects.get(pk=form.cleaned_data['cidade']),
				date_format='br', verbose=True)
			# TODO: redirect
			context["result"] = result
	context.update({"form": form, "naturezas": Natureza.objects.all()})
	return render(request, 'setup_app/inserir-ocorrencias.html', context)


def update_lat_lng(request):
	return render(request, 'setup_app/update_lat_lng.html')


def get_address(request):
	"Fetches Ocorrencia objects; returns them as json."
	queryset = Ocorrencia.objects.filter(latitude=0.0)[:100]
	if queryset.count() > 0:
		data = serializers.serialize('json', queryset)
	else:
		data = json.dumps({'end': 'Não existem mais lat e lng nulos.'})
	return HttpResponse(data, content_type='application/json')


def update_db(request):
	"/setup/update_db/ || Updates the Ocorrencia model."
	if request.method == 'POST':
		response_text = {'OK': ''}
		for pk, values in request.POST.items():
			try:
				row = Ocorrencia.objects.get(pk=pk)
				lat, lng = values.split(' ')
				if lat == 'null' or lng == 'null':
					lat, lng = None, None
				row.latitude = lat
				row.longitude = lng
				row.save()
				response_text['OK'] += 'Id %s atualizada<br />' % pk
			except ValueError:
				continue
		return HttpResponse(json.dumps(response_text),
			content_type="application/json")


### helper functions

def read_csv_file(f):

	return csv.reader(StringIO(f.read().decode("utf-8")),
					  delimiter=",")


### Forms

class RecordsFileForm(forms.Form):
	CITIES = Cidade.objects.all()

	cidade = forms.ModelChoiceField(queryset=CITIES, required=True)
	arquivo = forms.FileField(required=True)
