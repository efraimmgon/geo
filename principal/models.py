from django.db import models

# Create your models here.
class ExternalSources(models.Model):

	name = models.CharField(max_length=256)
	description = models.TextField(default='')
	link = models.URLField()

	def __str__(self):
		return self.name