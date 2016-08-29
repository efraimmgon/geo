from django.db import models

import datetime

from analise_criminal.utils import WEEKDAYS


class Cidade(models.Model):

	nome = models.CharField(max_length=200, default="unknown")

	def __str__(self):
		return self.nome


class Natureza(models.Model):

	nome = models.CharField(max_length=200, default="unknown")

	def __str__(self):
		return self.nome


class Ocorrencia(models.Model):

	# TODO: remove `natureza` field

	data = models.DateField(default=None, null=True)
	cidade = models.ForeignKey(Cidade, related_name="cidade", null=True, default=None)
	local = models.CharField(max_length=200, null=True, default=None)
	bairro = models.CharField(max_length=200, null=True, default=None)
	via = models.CharField(max_length=200, null=True, default=None)
	numero = models.CharField(max_length=200, null=True, default=None)
	latitude = models.FloatField(default=0, null=True)
	longitude = models.FloatField(default=0, null=True)
	naturezas = models.ForeignKey(Natureza, related_name='naturezas', null=True, default=None)
	natureza = models.CharField(max_length=200, null=True, default=None)
	hora = models.TimeField(default=None, null=True)
	periodo = models.CharField(max_length=200, null=True, default=None)

	def __str__(self):
		return ', '.join([self.naturezas.nome, str(self.data)])

	def date2string(self):
		return self.data.strftime('%d/%m/%Y')

	def weekday(self):
		return WEEKDAYS[ self.data.weekday() ]
