from django.conf.urls import url
from . import views

from .feeds import Feed


urlpatterns = [
    # ...
    url(r'(?P<customer_key>.*)/interface$', views.interface, name='interface'),
    url(r'(?P<customer_key>.*)/interface/(?P<date_stamp>.*)$', views.interface, name='interface'),
    url(r'(?P<customer_key>.*)/feed/latest$', Feed()),
    url(r'(?P<customer_key>.*)/feed/latest/(?P<selected_option>.*)$', Feed()),
    url(r'(?P<customer_key>.*)/feed/(?P<date>.*)$', Feed()),

    # ...
]
