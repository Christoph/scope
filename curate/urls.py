from django.conf.urls import url
from . import views

from .feeds import Feed
from django.conf.urls import include
from controlcenter.views import controlcenter

urlpatterns = [
    # ...
    
    url(r'(?P<customer_key>.*)/interface$', views.interface, name='interface_with_key'),
    url(r'(?P<customer_key>.*)/interface/(?P<date_stamp>.*)$', views.interface, name='interface_with_stamp'),
    url(r'(?P<customer_key>.*)/feed/latest$', Feed()),
    url(r'(?P<customer_key>.*)/feed/latest/(?P<selected_option>.*)$', Feed()),
    url(r'(?P<customer_key>.*)/feed/(?P<date>.*)$', Feed()),
    url(r'(?P<customer_key>.*)/mail$', views.mail, name='mail_with_key'),
    url(r'(?P<customer_key>.*)/dashboard/', include(controlcenter.urls_with_key)),
    url(r'dashboard/', include(controlcenter.urls)),
    url(r'interface$', views.interface, name='interface'),
    url(r'mail$', views.mail, name='mail'),

    # ...
]
