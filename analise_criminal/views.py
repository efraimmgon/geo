from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Min, Max, Count
from django.contrib.auth.decorators import login_required

import json
from collections import OrderedDict, defaultdict
from unicodedata import normalize

from setup_app.models import Ocorrencia
from .forms import (
	MapOptionForm, AdvancedOptionsForm, MapMarkerStyleForm,
	ReportForm, ReportFilterForm,
)
from .functions import (process_map_arguments, make_days_graph, 
	make_hours_graph, make_neighborhood_graph, make_street_graph,
	make_nature_graph)
from .report import (process_report_arguments, count_months, get_axis,
	nature_per_month_axis, return_naturezas_axis, ROUBO, HOM, TRAFICO)


def index(request):
	"""/analise_criminal/"""
	context = {}
	context['axis'] = OrderedDict()
	queryset = Ocorrencia.objects.filter(data__year=2015)
	xaxis, yaxis = get_axis(count_months(queryset))
	context['axis']['todas as ocorrências'] = {'x': xaxis, 'y': yaxis}

	## Something is wrong... it's not displaying the plotting.
	context.update(nature_per_month_axis(
			queryset=queryset, nats=(ROUBO, HOM, TRAFICO)))
	labels, values = return_naturezas_axis(queryset)

	context['axis']['pie'] = {'labels': labels, 'values': values}
	return render(request, 'index.html', context)

def lab(request):
	context = {}
	context['axis'] = OrderedDict()

	qs_days = Ocorrencia.objects.filter(data__gte='2016-01-01')
	context['axis']['dias'] = make_days_graph(queryset=qs_days,
		plot='bar', title='Registros por Dia', color='rgb(255,0,0)')

	qs = Ocorrencia.objects.filter(data__month=11)
	context['axis']['horas-nov'] = make_hours_graph(queryset=qs,
		plot='bar', title='Registros por hora Nov/15', color='rgb(0,255,0)')

	qs = Ocorrencia.objects.filter(data__lte='2016-01-01', data__gte='2015-12-01')
	context['axis']['horas-dez'] = make_hours_graph(queryset=qs,
		plot='bar', title='Registros por hora Dez/15', color='rgb(0,0,255)')

	qs = Ocorrencia.objects.filter(data__gte='2016-01-01')
	context['axis']['horas-jan'] = make_hours_graph(queryset=qs,
		plot='bar', title='Registros por hora Jan/16', color='rgb(255,255,0)')

	lst = [()]

	return render(request, 'analise_criminal/lab.html', context)

#@login_required
def map(request):
	"""/analise_criminal/mapa/"""
	return render(request, 'mapa.html')
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
