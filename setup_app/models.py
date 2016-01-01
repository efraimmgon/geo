from django.db import models

import datetime


class Ocorrencia(models.Model):

	data = models.DateField(default=None, null=True)
	local = models.CharField(max_length=200)
	latitude = models.FloatField(default=0)
	longitude = models.FloatField(default=0)
	natureza = models.CharField(max_length=200)
	hora = models.TimeField(default=None, null=True)

	def __str__(self):
		return self.natureza