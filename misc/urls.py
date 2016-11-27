from django.conf.urls import url
from . import views

urlpatterns = [
    # ...
    url(r'alive$',views.artsy,name='artsy'), 
    # ...
]