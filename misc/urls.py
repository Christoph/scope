from django.conf.urls import url
from . import views

urlpatterns = [
    # ...
    url(r'alive$',views.artsy,name='artsy'),
    url(r'test_task$',views.test_task_view,name='test_task_view'), 
    # ...
]