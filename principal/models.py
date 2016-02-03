from django.db import models


class Tag(models.Model):
	
	name = models.CharField("Nome", max_length=256, unique=True)
	description = models.TextField("Descrição", default='')

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "Marcador"
		verbose_name = "Marcadores"


class ExternalSource(models.Model):

	name = models.CharField("Nome", max_length=256, unique=True,
		default='')
	description = models.TextField("Descrição", default='')
	link = models.URLField()
	tags = models.ManyToManyField(Tag, verbose_name="Etiquetas")

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "Fonte externa"
		verbose_name_plural = "Fontes externas"