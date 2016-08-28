from django.contrib import admin

from .models import Ocorrencia, Natureza, Cidade
from principal.models import ExternalSource, Tag


class OcorrenciaAdmin(admin.ModelAdmin):
	
	fieldsets = [
		('Registro', {'fields': ['data', 'hora']}),
		('Localização', {'fields': ['bairro', 'via', 'numero', 
			'latitude', 'longitude']}),
		(None, {'fields': ['naturezas']}),
	]
	list_display = ('naturezas', 'bairro', 'via', 'data')
	list_filter = ['naturezas', 'data']
	search_fields = ['bairro', 'via', 'latitude']


admin.site.register(Natureza)
admin.site.register(Cidade)
admin.site.register(Ocorrencia, OcorrenciaAdmin)
admin.site.register(ExternalSource)
admin.site.register(Tag)