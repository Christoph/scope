"""graphite URL Configuration

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
from controlcenter.views import controlcenter
# from django.shortcuts import render
# from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^admin/dashboard/', include(controlcenter.urls)),
    # url(r'^admin/dashboard/(?P<query_pk>\d+)/', include(controlcenter.urls)),
    url(r'^curate/', include('curate.urls',namespace="curate")),
    url(r'^curate/dashboard/', include(controlcenter.urls)),
    url(r'^explore/', include('explore.urls',namespace="explore")),
    url(r'^', include('homepage.urls', namespace='homepage')),
    url(r'^misc/', include('misc.urls', namespace='misc')),
    url(r'^research/', include('research.urls', namespace='research')),
]

