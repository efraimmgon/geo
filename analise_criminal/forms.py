from django import forms

from setup_app.models import Ocorrencia
from analise_criminal.functions import add_venue_hood

class MapOptionForm(forms.Form):

	naturezas = Ocorrencia.objects.values('natureza').distinct()
	choices = (
		('selecione', 'Selecione'),
		('todas', 'Todas'),
	)

	for n in naturezas:
		choices += ( (n['natureza'], n['natureza']), )


	natureza = forms.ChoiceField(
		label='Natureza', choices=choices, required=True
	)
	data_inicial = forms.DateField(
		label='Data inicial',
		input_formats=['%d/%m/%Y', '%d/%m/%y'], required=True,
		widget=forms.DateInput(attrs={'placeholder': 'dd/mm/aaaa'})
	)
	data_final = forms.DateField(
		label='Data final',
		input_formats=['%d/%m/%Y', '%d/%m/%y'], required=True,
		widget=forms.DateInput(attrs={'placeholder': 'dd/mm/aaaa'})
	)


class AdvancedOptionsForm(forms.Form):
	
	bairro = forms.CharField(label='Bairro', required=False,
		help_text="Campo opcional."
	)
	via = forms.CharField(label='Via', required=False, 
		help_text="Campo opcional."
	)
	hora_inicial = forms.TimeField(
		label='Hora inicial', required=False, input_formats=['%H:%M'],
		help_text="Campo opcional.",
		widget=forms.TimeInput(attrs={'placeholder': 'hh:mm'})
	)
	hora_final = forms.TimeField(
		label='Hora final', required=False, input_formats=['%H:%M'],
		help_text="Campo opcional.",
		widget=forms.TimeInput(attrs={'placeholder': 'hh:mm'})
	)


class MapMarkerStyleForm(forms.Form):

	styles = (
		('basicMarker', 'Marcador básico'),
		('heatmap', 'Mapa de calor'),
	)

	marker_style = forms.ChoiceField(
		label="Tipo de marcador", choices=styles
	)




