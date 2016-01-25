from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Min, Max
from django.contrib.auth.decorators import login_required

import json

from setup_app.models import Ocorrencia
from .forms import (
	MapOptionForm, AdvancedOptionsForm, MapMarkerStyleForm,
	ReportForm, ReportFilterForm,
)
from .functions import process_map_arguments
from .report import process_report_arguments, get_months, get_month_axis

from reportlab.pdfgen import canvas
from django.http import HttpResponse
def index(request):
	o = Ocorrencia.objects.all()
	months = get_months(o)
	xaxis, yaxis = get_month_axis(months)
	context = {
		'x': xaxis,
		'y': yaxis
	}
	return render(request, 'analise_criminal/index.html', context)


@login_required
def map(request):
	"""/analise_criminal/mapa/"""
	form_styles = MapMarkerStyleForm()
	form_options = MapOptionForm()
	form_advanced_options = AdvancedOptionsForm()

	queryset = Ocorrencia.objects.all() 
	mindata = queryset.aggregate(Min('data'))
	maxdata = queryset.aggregate(Max('data'))

	context = {
		'form_options': form_options, 'form_styles': form_styles,
		'form_advanced': form_advanced_options,
		'min': mindata['data__min'].strftime('%d/%m/%Y'), 
		'max': maxdata['data__max'].strftime('%d/%m/%Y')
	}

	return render(request, 'analise_criminal/mapa.html', context)


def mapAjax(request):
	if request.method == 'POST':
		form = MapOptionForm(data=request.POST)
		form_advanced = AdvancedOptionsForm(data=request.POST)
		if form.is_valid() and form_advanced.is_valid():
			json_data = process_map_arguments(form, form_advanced)
		else:
			## refactor forms.py to have portuguese errors.
 	 		json_data = json.dumps({'errors': form.errors})
	
	return HttpResponse(json_data, content_type='application/json')


@login_required
def report(request):
	form_report = ReportForm()
	form_filter = ReportFilterForm()
	context = {'form_report': form_report, 'form_filter': form_filter}
	return render(request, 'analise_criminal/relatorio.html', context)


@login_required
def make_report(request):
	form_report = ReportForm(data=request.GET)
	form_filter = ReportFilterForm(data=request.GET)
	context = {}
	if form_report.is_valid() and form_filter.is_valid():
		context = process_report_arguments(form_report, form_filter)
	else:
		context = {'form_report': form_report, 'form_filter': form_filter}
	
	return render(request, 'analise_criminal/relatorio.html', context)
