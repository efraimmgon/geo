from django.conf.urls import url, patterns
from setup_app import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^ajaxTest/$', views.ajaxTest, name='ajaxTest'),
	url(r'^update_lat_lng/$', views.update_lat_lng, name='update_lat_lng'),
	url(r'^get_address/$', views.get_address, name='get_address'),
	url(r'^update_db/$', views.update_db, name='update_db'),
]