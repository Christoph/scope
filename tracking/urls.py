from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        "^open/(?P<path>[\w=-]+)/$", views.MyOpenTrackingView.as_view(),
        name="open_tracking"),
    url(
        "^click/(?P<path>[\w=-]+)/$", views.MyClickTrackingView.as_view(),
        name="click_tracking"),
]