from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.utils.decorators import method_decorator
from django.utils.module_loading import import_string
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from scope.models import UserProfile
from . import app_settings


class ControlCenter(object):

    def __init__(self, view_class):
        self.view_class = view_class

    def get_dashboards(self):
        klasses = map(import_string, app_settings.DASHBOARDS)
        dashboards = [klass(pk=pk) for pk, klass in enumerate(klasses)]
        if not dashboards:
            raise ImproperlyConfigured('No dashboards found.')
        return dashboards

    def get_view(self):
        dashboards = self.get_dashboards()
        return self.view_class.as_view(dashboards=dashboards)

    def get_urls(self):
        urlpatterns = [
            url(r'^(?P<pk>\d+)/$', self.get_view(), name='dashboard'),
        ]
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), 'controlcenter', 'controlcenter'

    @property
    def urls_with_key(self):
        return self.get_urls(), 'controlcenter_with_key', 'controlcenter_with_key'



# def user_corresponds_to_customer_key(user):
#     user_profile = UserProfile.objects.get(user=request.user)
#     return customer_key == user_profile.customer.customer_key:
#     pass


class DashboardView(LoginRequiredMixin, TemplateView): #UserPassesTestMixin,

    dashboards = NotImplemented
    template_name = 'controlcenter/dashboard.html'
    # def determine_login_path(self):
    #     return redirect('/login/?next=%s' % self.request.path)

    # login_url = 
    # @method_decorator(staff_member_required)
    # def test_func(self):
    #     try:
    #         user_profile = UserProfile.objects.get(user=self.request.user)
    #         customer_key = self.kwargs['customer_key']
    #         return customer_key == user_profile.customer.customer_key
    #     except:
    #         return False

    def dispatch(self, *args, **kwargs):
        return super(DashboardView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        pk = int(self.kwargs['pk'])
        if self.request.user.is_superuser:
            try:
                customer_key = self.kwargs['customer_key']
            except:
                return redirect('/admin')
        else:
            user_profile = UserProfile.objects.get(user=self.request.user)
            customer_key = user_profile.customer.customer_key

        for dashboard in self.dashboards:
                dashboard.add_customer_key(customer_key)
        try:
            self.dashboard = self.dashboards[pk]
        except IndexError:
            raise Http404('Dashboard not found.')
        return super(DashboardView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        if self.request.user.is_superuser:
            customer_key = self.kwargs['customer_key']
        else: 
            user_profile = UserProfile.objects.get(user=self.request.user)
            customer_key = user_profile.customer.customer_key
        options = {'customer_key': customer_key}
        context = {
            'customer_key': customer_key,
            'title': self.dashboard.title,
            'dashboard': self.dashboard,
            'dashboards': self.dashboards,
            'groups': self.dashboard.get_widgets(self.request, **options),
            'sharp': app_settings.SHARP,
        }

        # Admin context
        kwargs.update(admin.site.each_context(self.request))
        kwargs.update(context)
        return super(DashboardView, self).get_context_data(**kwargs)


controlcenter = ControlCenter(view_class=DashboardView)
