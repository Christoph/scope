from django.conf.urls import url
from . import views

urlpatterns = [
    # ...
    url(r'customsearch$', views.customsearch, name='customsearch'),
    url(r'cs=(?P<strin>.*)$', views.custom_results, name='csr'),
    url(r'mobile$',views.mobile,name='mobile'),
    url(r'^$', views.home, name='home'),
    url(r'^update_state$', views.update_state, name="update_state"),
   	url(r'^search_task_term$', views.search_task_term, name="search_task_term"),
   	url(r'^search_task_feeds$', views.search_task_feeds, name="search_task_feeds"),
   	url(r'^alert', views.alert, name='alert'),
   	url(r'^mobile',views.mobile,name='mobile'),  
    # ...
]