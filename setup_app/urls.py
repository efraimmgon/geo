from django.conf.urls import url, patterns
from setup_app import views

urlpatterns = [
	# index test page
	url(r'^$', views.index, name='index'),
	# ajax request from index
	url(r'^ajaxTest/$', views.ajaxTest, name='ajaxTest'),
	url(r'^update-lat-lng/$', views.update_lat_lng, name='update_lat_lng'),
	# ajax get request from update_lat_lng
	url(r'^get-address/$', views.get_address, name='get_address'),
	# AJAX POST: sync rows address with lat and long
	url(r'^update-db/$', views.update_db, name='update_db'),
	# POST: Insert rows in Ocorrencia model
	url(r'^incluir-ocorrencias/$', views.insert_records, name='insert_records'),
]