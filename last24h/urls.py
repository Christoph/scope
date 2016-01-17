from django.conf.urls import url
#from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    # ex: /last24h/
    url(r'^$', views.index, name='index'),
    # /last24h/custom_search
    url(r'q=(?P<topic>.*)$', views.csresults, name='csresults'),#kwargs = {'topic':topic}),#\?q=(?P<topic>\w+)$', views.csresults, name='csresults'),

]
