from django.conf.urls import url
from . import views

from .feeds import Feed


urlpatterns = [
    # ...
    url(r'(?P<customer_key>.*)/interface$', views.interface, name='interface'),
    url(r'(?P<customer_key>.*)/feed/latest$', Feed()),

    # ...
]
