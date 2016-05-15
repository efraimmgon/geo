from django import forms


class TimeDeltaForm(forms.Form):
	data_inicial = forms.DateField(
		label='Data de início do gozo/afastamento',
		input_formats=['%d/%m/%Y', '%d/%m/%y'], required=True,
		widget=forms.DateInput(attrs={'placeholder': 'dd/mm/aaaa', 'class': 'form-control'}))
	dias = forms.IntegerField(
		label='Dias de gozo/afastamento', required=True)