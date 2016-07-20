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
    url(r'^landing', views.landing, name='landing'),
    url(r'^last24h/', include('last24h.urls', namespace='last24h')),
    url(r'^$', views.home, name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^about/', views.about, name = 'about'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^disclaimer/', views.disclaimer, name = 'disclaimer'),
    url(r'^register/', views.register, name = 'register'),
    url(r'^confirm/(?P<activation_key>.*)$', views.confirm, name = 'confirm'),
    url(r'^profile/', views.profile, name = 'profile'),
    url(r'cs=(?P<strin>.*)$', views.custom_results, name='csr'),#kwargs = {'topic':topic}),#\?q=(?P<topic>\w+)$', views.csresults, name='csresults'),
    url(r'custom-search$', views.customsearch, name='customsearch'),#kwargs = {'topic':topic}),#\?q=(?P<topic>\w+)$', views.csresults, name='csresults'),
    url(r'^about', views.about, name='about'),
    url(r'^mobile',views.mobile,name='mobile'),  
    url(r'^grews-alert', views.grews_alert, name='grews_alert'),
    url(r'^how-it-works', views.how_it_works, name='how_it_works'),
    url(r'^server_error$', views.server_error, name = 'server_error'),
    url(r'^login$', views.login_user, name = 'login_user'),
    url(r'^logout$', views.logout_user, name = 'logout_user'),
    #url(r'^password$', views.password, name = 'password'),
    url(r'^profile_delete$', views.profile_delete, name = 'profile_delete'),
    url(r'^profile_edit$', views.profile_edit, name = 'profile_edit'),
    url(r'^alert_edit$', views.alert_edit, name = 'alert_edit'),
    url(r'^contact$', views.contact, name = 'contact'), 
    url(r'mobile$',views.mobile,name='mobile'),   
   url(r'alive$',views.artsy,name='artsy'),   
   url(r'happybday$',views.martin,name='martin'),
   #url(r'^search_state$', views.search_state, name="search_state"),
   url(r'^update_state$', views.update_state, name="update_state"),
   url(r'^search_task_term$', views.search_task_term, name="search_task_term"),
   url(r'^search_task_feeds$', views.search_task_feeds, name="search_task_feeds"),
   url(r'^send_sample$', views.send_sample, name="send_sample"),
]

