from django.contrib import admin

from .models import Ocorrencia
from principal.models import ExternalSource, Tag


class OcorrenciaAdmin(admin.ModelAdmin):
	
	fieldsets = [
		('Registro', {'fields': ['data', 'hora']}),
		('Localização', {'fields': ['bairro', 'via', 'numero', 
			'latitude', 'longitude']}),
		(None, {'fields': ['natureza']}),
	]

	list_display = ('natureza', 'bairro', 'via', 'data')
	list_filter = ['natureza', 'data']
	search_fields = ['bairro', 'via', 'latitude']


admin.site.register(Ocorrencia, OcorrenciaAdmin)
admin.site.register(ExternalSource)
admin.site.register(Tag)