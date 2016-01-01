from django.contrib import admin

from .models import Ocorrencia


class OcorrenciaAdmin(admin.ModelAdmin):
	
	fieldsets = [
		('Registro', {'fields': ['data', 'hora']}),
		('Localização', {'fields': ['local', 'latitude', 'longitude']}),
		(None, {'fields': ['natureza']}),
	]

	list_display = ('natureza', 'local', 'data')
	list_filter = ['natureza', 'data']
	search_fields = ['local', 'latitude']


admin.site.register(Ocorrencia, OcorrenciaAdmin)