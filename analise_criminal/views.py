from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Min, Max
from django.contrib.auth.decorators import login_required

import json
from collections import OrderedDict
from unicodedata import normalize

from setup_app.models import Ocorrencia
from .forms import (
	MapOptionForm, AdvancedOptionsForm, MapMarkerStyleForm,
	ReportForm, ReportFilterForm,
)
from .functions import process_map_arguments
from .report import (process_report_arguments, get_months, get_month_axis, 
	return_months_axis, return_naturezas_axis)


def index(request):
	"""/analise_criminal/"""
	context = {}
	context['axis'] = OrderedDict()
	queryset = Ocorrencia.objects.filter(data__year=2015)
	xaxis, yaxis = get_month_axis(get_months(queryset))
	context['axis']['todas as ocorrências'] = {'x': xaxis, 'y': yaxis}

	context = return_months_axis(
		queryset=queryset,
		filters=['roubo', 'furto', normalize('NFKD', 'homicídio'), 
		normalize('NFKD', 'tráfico ilícito de drogas')],
		context=context
	)
	labels, values = return_naturezas_axis(
		queryset=queryset,
		filters=['roubo', 'furto', normalize('NFKD', 'homicídio'), 
		normalize('NFKD', 'tráfico ilícito de drogas'), 'outros']
	)
	context['axis']['pie'] = {'labels': labels, 'values': values}
	return render(request, 'analise_criminal/index.html', context)


@login_required
def map(request):
	"""/analise_criminal/mapa/"""
	queryset = Ocorrencia.objects.all()
	## Min and max date where search is available:
	mindata = queryset.aggregate(Min('data'))
	maxdata = queryset.aggregate(Max('data'))
	context = {
		'form_options': MapOptionForm(),
		'form_styles': MapMarkerStyleForm(),
		'form_advanced': AdvancedOptionsForm(),
		'min': mindata['data__min'].strftime('%d/%m/%Y'), 
		'max': maxdata['data__max'].strftime('%d/%m/%Y')
	}
	return render(request, 'analise_criminal/mapa.html', context)


def mapAjax(request):
	"""
	/analise_criminal/mapAjax/
	Returns the necessary data, via AJAX, to generate the markers
	at /analise_criminal/mapa/.
	"""
	if request.method == 'POST':
		form_options = MapOptionForm(data=request.POST)
		form_advanced = AdvancedOptionsForm(data=request.POST)
		if form_options.is_valid() and form_advanced.is_valid():
			json_data = process_map_arguments(form_options, form_advanced)
		else:
			## refactor forms.py to have errors in portuguese.
 	 		json_data = json.dumps({'errors': form_options.errors})
	return HttpResponse(json_data, content_type='application/json')


@login_required
def report(request):
	"""
	/analise_criminal/relatorio/
	Renders a page where the user can select a period and other record options,
	which will be sent to make_report and used to generate a report.
	"""
	context = {
		'forms': {'report': ReportForm(), 'filter': ReportFilterForm()}
	}
	return render(request, 'analise_criminal/relatorio.html', context)


@login_required
def make_report(request):
	"""
	/analise_criminal/make_report/
	Takes some info about records and renders a report based on that info.
	"""
	form_report = ReportForm(data=request.GET)
	form_filter = ReportFilterForm(data=request.GET)
	context = {}
	if form_report.is_valid() and form_filter.is_valid():
		context = process_report_arguments(form_report, form_filter)
	else:
		context = {'form_report': form_report, 'form_filter': form_filter}
	return render(request, 'analise_criminal/relatorio.html', context)

@login_required
def draggable(request):
	"""
	/analise_criminal/draggable/
	Renders a page with a google map, allowing the dragging of objs and their
	setting on a new lat and lng.
	"""
	if str(request.user) != 'efraimmgon':
		denied = "%s: você não tem permissão para acessar esta página"
		return HttpResponse(denied % request.user)
	updated = []
	if request.method == 'POST':
		for pk, values in request.POST.items():
			try:
				row = Ocorrencia.objects.get(pk=pk)
				_, lat, lng = values.split()
				row.latitude = lat
				row.longitude = lng
				row.save()
				updated.append(pk)
			except ValueError:
				continue
	context = {
		'form_options': MapOptionForm(),
		'form_styles': MapMarkerStyleForm(),
		'form_advanced': AdvancedOptionsForm(),
		'updated': updated
	}
	return render(request, 'analise_criminal/draggable.html', context)
