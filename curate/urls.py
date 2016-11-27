from django.conf.urls import url
from . import views

from .feeds import Feed


urlpatterns = [
    # ...
    url(r'^$', views.interface,name="interface"),
    url(r'^feed/latest$', Feed()),
    
    # ...
]