from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers

from setup_app.models import Ocorrencia
from setup_app.functions import dump_object


def index(request):
	"""Home for testing code"""
	o = Ocorrencia.objects.all()[100:110]
	return render(request, 'setup_app/test.html', context={'ocorrencias': o})

def ajaxTest(request):
	"""Testing code"""
	if request.method == 'POST':
		test_data = request.POST.get('test')
		if test_data:
			return HttpResponse(test_data)
		else:
			return HttpResponse("Test data is not set")

def update_lat_lng(request):
	"""Renders the template to begin the update"""
	return render(request, 'setup_app/update_lat_lng.html')

def get_address(request):
	"""Fetches Ocorrencia objects and returns them as json."""
	if request.method == 'GET':
		stop = int(request.GET.get('stop'))
		if stop == 0:
			o = Ocorrencia.objects.all().filter(latitude=0.0)[:10]
		else:
			o = Ocorrencia.objects.all()
			o = o.filter(pk__gt=stop).filter(latitude=0.0)[:10]
		
		if o.count() > 0:
			data = serializers.serialize('json', o)
			return HttpResponse(data, content_type='application/json')
		else:
			return HttpResponse(None)

def update_db(request):
	"""Updates the Ocorrencia model"""
	if request.method == 'POST':
		if request.POST.get('start') and request.POST.get('stop'):
			start = int(request.POST.get('start'))
			stop = int(request.POST.get('stop'))

			stop += 1
			response_text = ''
			for i in range(start, stop):
				update = request.POST.get('loc-%s' % (i,))
				if update:
					pk, lat, lng = update.split(' ')
					o = Ocorrencia.objects.get(pk=pk)
					## Doubt
					o.latitude = lat
					o.longitude = lng
					o.save()
					response_text += 'Pk %s atualizada <br />' % (pk,)
				else:
					response_text += "loc-%s is not set <br />" % (i,)
			return HttpResponse(response_text)
		else:
			return HttpResponse("Range start and stop is not set")