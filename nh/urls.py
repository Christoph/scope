from django.conf.urls import url
from . import views

from nh.feeds import Feed_NH


urlpatterns = [
    # ...
    url(r'^$', views.interface,name="interface"),
    url(r'^feed/latest$', Feed_NH()),
    # ...
]