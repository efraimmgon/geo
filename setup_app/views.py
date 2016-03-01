from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers

import json

from setup_app.models import Ocorrencia
from setup_app.functions import dump_object


def index(request):
	"""
	/setup/
	Home for testing code
	"""
	return render(request, 'setup_app/index.html')

def ajaxTest(request):
	"""
	/setup/ajaxTest/
	Testing code
	"""
	queryset = Ocorrencia.objects.filter(latitude=0.0)[:20]
	if queryset.count() > 0:
		data = serializers.serialize('json', queryset)	
	else:
		data = json.dumps({'end': 'Não existem mais lat e lng nulos.'})
	return HttpResponse(data, content_type='application/json')

def update_lat_lng(request):
	"""
	/setup/update_lat_lng/
	Renders the template to begin the update
	"""
	return render(request, 'setup_app/update_lat_lng.html')

def get_address(request):
	"""
	/setup/get_address/
	Fetches Ocorrencia objects; returns them as json.
	"""
	if request.method == 'GET':
		queryset = Ocorrencia.objects.filter(latitude=0.0)[:100]
		if queryset.count() > 0:
			data = serializers.serialize('json', queryset)	
		else:
			data = json.dumps({'end': 'Não existem mais lat e lng nulos.'})
		return HttpResponse(data, content_type='application/json')
	
	

def update_db(request):
	"""
	/setup/update_db/
	Updates the Ocorrencia model
	"""
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
				response_text['OK'] += 'Id %s atualizada<br />' % (pk,)
			except ValueError:
				continue
		return HttpResponse(json.dumps(response_text), 
			content_type="application/json")
