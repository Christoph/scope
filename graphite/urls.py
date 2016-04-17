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
from django.shortcuts import render
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
#    url(r'^djga/', include('google_analytics.urls')),
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^', include('last24h.urls')),
    url(r'^$', views.index, name='index'),
    url(r'^last24h/', include('last24h.urls', namespace='last24h')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^about/', views.about, name = 'about'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^disclaimer/', views.disclaimer, name = 'disclaimer'),
    url(r'^register/', views.register, name = 'register'),
    url(r'^confirm/(?P<activation_key>.*)$', views.confirm, name = 'confirm'),
    url(r'^profile/', views.profile, name = 'profile'),
    url(r'cs=(?P<strin>.*)$', views.csr, name='csr'),#kwargs = {'topic':topic}),#\?q=(?P<topic>\w+)$', views.csresults, name='csresults'),
    url(r'custom-search$', views.customsearch, name='customsearch'),#kwargs = {'topic':topic}),#\?q=(?P<topic>\w+)$', views.csresults, name='csresults'),
    url(r'^about', views.about, name='about'),
    url(r'^grews-alert', views.grews_alert, name='grews_alert'),
    url(r'^how-it-works', views.how_it_works, name='how_it_works'),
    url(r'^server_error$', views.server_error, name = 'server_error'),
    url(r'^login$', views.login_user, name = 'login_user'),
    url(r'^logout$', views.logout_user, name = 'logout_user'),
    #url(r'^password$', views.password, name = 'password'),
    url(r'^profile_delete$', views.profile_delete, name = 'profile_delete'),
    url(r'^contact$', views.contact, name = 'contact'),
   url(r'artsy$',views.artsy,name='artsy'),   
   url(r'happybday$',views.martin,name='martin'),
   #url(r'^search_state$', views.search_state, name="search_state"),
   url(r'^update_state$', views.update_state, name="update_state"),
   url(r'^search_task_term$', views.search_task_term, name="search_task_term"),
   url(r'^search_task_feeds$', views.search_task_feeds, name="search_task_feeds"),
]

