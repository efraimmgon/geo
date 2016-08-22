from django.conf.urls import url
from analise_criminal import views

# root: /analise_criminal/
urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^mapa/$', views.map, name='map'),
	url(r'^mapAjax/$', views.mapAjax, name='mapAjax'),
	url(r'^relatorio/$', views.report, name='report'),
	url(r'^gerar-relatorio/$', views.make_report, name='gerar_relatorio'),
	url(r'^draggable/$', views.draggable, name='draggable'),
	url(r'^lab/$', views.lab, name='lab'),
]