from django import forms

from setup_app.models import Ocorrencia, Cidade
from .commons import (
	NATUREZAS, NATUREZAS_ID_ALL, ROUBO, FURTO, TRAFICO, HOMICIDIO,
	DROGAS)
from .utils import lmap, lfilter

CITIES = Cidade.objects.all()

class PlottingForm(forms.Form):

	choices_tipo = [('bar', 'Coluna'),
					('pie', 'Pizza'),
					('scatter', 'Ponto')]

	choices_campo = [
		('naturezas', 'Natureza'),
		('bairro', 'Bairro'),
		('via', 'Via'),
		('dia da semana', 'Dia da Semana'),
		('dia', 'Dia'),
		('mês', 'Mês'),
	]

	tipo = forms.ChoiceField(
		label="Tipo de Gráfico", choices=choices_tipo, required=True)
	campo = forms.ChoiceField(choices=choices_campo, required=True)
	data_inicial = forms.DateField(
		label='Data inicial',
		input_formats=['%d/%m/%Y', '%d/%m/%y'], required=True,
		widget=forms.DateInput(
			attrs={'placeholder': 'dd/mm/aaaa', 'class': 'form-control'}))
	data_final = forms.DateField(
		label='Data final',
		input_formats=['%d/%m/%Y', '%d/%m/%y'], required=True,
		widget=forms.DateInput(
			attrs={'placeholder': 'dd/mm/aaaa', 'class': 'form-control'}))

	# natureza = forms.ModelChoiceField(queryset)
	# bairro
	# rua
	# dia_da_semana
	# dia
	# mes
	# ano


class MapOptionForm(forms.Form):

	choices = [
		("", "Selecione"),
		("todas", "Todas"),
		(DROGAS, "Entorpecentes"),
		(HOMICIDIO, "Homicídio"),
	]

	choices += lmap(lambda n: (n.pk, n.nome), NATUREZAS)

	cidade = forms.ModelChoiceField(queryset=CITIES, required=True)
	natureza = forms.ChoiceField(
		label='Natureza', choices=choices, required=True)
	data_inicial = forms.DateField(
		label='Data inicial',
		input_formats=['%d/%m/%Y', '%d/%m/%y'], required=True,
		widget=forms.DateInput(
			attrs={'placeholder': 'dd/mm/aaaa', 'class': 'form-control'}))
	data_final = forms.DateField(
		label='Data final',
		input_formats=['%d/%m/%Y', '%d/%m/%y'], required=True,
		widget=forms.DateInput(
			attrs={'placeholder': 'dd/mm/aaaa', 'class': 'form-control'}))


class AdvancedOptionsForm(forms.Form):

	bairro = forms.CharField(label='Bairro', required=False,
		help_text="Campo opcional.",
		widget=forms.TextInput(attrs={'class': 'form-control'}))
	via = forms.CharField(label='Via', required=False,
		help_text="Campo opcional.",
		widget=forms.TextInput(attrs={'class': 'form-control'}))
	hora_inicial = forms.TimeField(
		label='Hora inicial', required=False, input_formats=['%H:%M'],
		help_text="Campo opcional.",
		widget=forms.TimeInput(
			attrs={'placeholder': 'hh:mm', 'class': 'form-control'}))
	hora_final = forms.TimeField(
		label='Hora final', required=False, input_formats=['%H:%M'],
		help_text="Campo opcional.",
		widget=forms.TimeInput(
			attrs={'placeholder': 'hh:mm', 'class': 'form-control'}))


class MapMarkerStyleForm(forms.Form):

	styles = (
		('basicMarker', 'Marcador básico'),
		('heatmap', 'Mapa de calor'))

	marker_style = forms.ChoiceField(
		label="Tipo de marcador", choices=styles)


class ReportForm(forms.Form):

	data_inicial_a = forms.DateField(
		input_formats=['%d/%m/%Y', '%d/%m/%y'], required=True,
		widget=forms.DateInput(
			attrs={'placeholder': 'dd/mm/aaaa', 'class': 'form-control'}))
	data_final_a = forms.DateField(
		input_formats=['%d/%m/%Y', '%d/%m/%y'], required=True,
		widget=forms.DateInput(
			attrs={'placeholder': 'dd/mm/aaaa', 'class': 'form-control'}))

	data_inicial_b = forms.DateField(
		input_formats=['%d/%m/%Y', '%d/%m/%y'], required=True,
		widget=forms.DateInput(
			attrs={'placeholder': 'dd/mm/aaaa', 'class': 'form-control'}))
	data_final_b = forms.DateField(
		input_formats=['%d/%m/%Y', '%d/%m/%y'], required=True,
		widget=forms.DateInput(
			attrs={'placeholder': 'dd/mm/aaaa', 'class': 'form-control'}))

	choices = (
		('Sim', 'Sim'),
		('Não', 'Não'),
	)

	opts = forms.ChoiceField(required=False,
		label='Gerar análise principal?', choices=choices)

class ReportFilterForm(forms.Form):

	choices = (
		(ROUBO, 'Roubo'),
		(FURTO, 'Furto'),
		(TRAFICO, 'Tráfico'),
		(HOMICIDIO, 'Homicídio'),
	)

	cidade = forms.ModelChoiceField(queryset=CITIES, required=True)
	naturezas = forms.MultipleChoiceField(required=False,
		widget=forms.CheckboxSelectMultiple, choices=choices)
	bairro = forms.CharField(label='Bairro', required=False,
		widget=forms.TextInput(attrs={'class': 'form-control'}))

	choices_opts = (
		('weekdays', 'Dias da semana'),
		('time', 'Horários'),
	)

	details = forms.MultipleChoiceField(required=False, label='Detalhamentos',
		widget=forms.CheckboxSelectMultiple, choices=choices_opts)
