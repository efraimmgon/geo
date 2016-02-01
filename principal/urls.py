from django.conf.urls import url
from principal import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^biblioteca/$', views.biblioteca, name='biblioteca'),
]