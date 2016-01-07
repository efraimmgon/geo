from django.db import models

import datetime



class Ocorrencia(models.Model):

	weekdays = {
		0: 'Segunda',
		1: 'Terça',
		2: 'Quarta',
		3: 'Quinta',
		4: 'Sexta',
		5: 'Sábado',
		6: 'Domingo'
	}

	data = models.DateField(default=None, null=True)
	local = models.CharField(max_length=200)
	bairro = models.CharField(max_length=200, null=True, default=None)
	via = models.CharField(max_length=200, null=True, default=None)
	numero = models.CharField(max_length=200, null=True, default=None)
	latitude = models.FloatField(default=0)
	longitude = models.FloatField(default=0)
	natureza = models.CharField(max_length=200)
	hora = models.TimeField(default=None, null=True)

	def __str__(self):
		return self.natureza
