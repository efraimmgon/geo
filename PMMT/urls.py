"""PMMT URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from principal import urls as principal_urls
from setup_app import urls as setup_urls
from analise_criminal import urls as analise_urls
from escala import urls as escala_urls
from accounts import urls as accounts_urls

urlpatterns = [
    url(r'^', include(principal_urls, namespace='principal')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^setup/', include(setup_urls, namespace="setup")),
    url(r'^analise_criminal/', include(analise_urls, 
        namespace="analise_criminal")),
    url(r'^escala/', include(escala_urls, namespace='escala')),
    url(r'^accounts/', include(accounts_urls, namespace='accounts')),
]

# unsuitable for production; for development only!
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, 
        document_root=settings.MEDIA_ROOT)

# for production
if not settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, 
		document_root=settings.STATIC_ROOT)