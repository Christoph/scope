from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.landing, name = 'landing'),
    url(r'^disclaimer/', views.disclaimer, name = 'disclaimer'),
    url(r'^register/', views.register, name = 'register'),
    url(r'^confirm/(?P<activation_key>.*)$', views.confirm, name = 'confirm'),
    url(r'^profile/', views.profile, name = 'profile'),
    url(r'^how-it-works', views.how_it_works, name='how_it_works'),
    url(r'^server_error$', views.server_error, name = 'server_error'),
    # url(r'^login/', views.login, name = 'login'),
    url(r'^logout/', views.logout_user, name = 'logout'),
    url(r'^profile_delete$', views.profile_delete, name = 'profile_delete'),
    url(r'^profile_edit$', views.profile_edit, name = 'profile_edit'),
    url(r'^alert_edit$', views.alert_edit, name = 'alert_edit'),
    url(r'^contact$', views.contact, name = 'contact'),
    url(r'^contact_landing$', views.contact_landing, name = 'contact_landing'),
    url(r'^send_sample$', views.send_sample, name="send_sample"),

]