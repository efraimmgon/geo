from django.conf.urls import url
from analise_criminal import views

urlpatterns = [
	url(r'^mapa/$', views.map, name='map'),
	url(r'^mapAjax/$', views.mapAjax, name='mapAjax'),
]