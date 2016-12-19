from django.contrib.syndication.views import Feed
from django.urls import reverse

#from .models import Select

from datetime import date

from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer
from scope.models import Customer, UserProfile


class Feed(Feed):
    title = "Today's NHBrief"
    link = "/nh/"
    description = "Daily neulandherzer newsletter"

    def get_object(self, request, customer_key):
        return Customer.objects.get(customer_key=customer_key)

    def items(self, obj):
        # user_profile = UserProfile.objects.get(user=request.user)
        # customer_key == user_profile.customer.customer_key:
        # print customer_key
        # customer = Customer.objects.get(customer_key=customer_key)
        print obj
        curate_customer = Curate_Customer.objects.get(customer=obj)
        last_query = Curate_Query.objects.filter(curate_customer=curate_customer).filter(time_stamp=date.today()).order_by("pk").reverse()[0]
        article_query_instances = Article_Curate_Query.objects.filter(curate_query=last_query).filter(is_selected=True).order_by("rank")
        suggestions = [i.article for i in article_query_instances]

        print Article_Curate_Query.objects.filter(curate_query=last_query)

        return suggestions

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.body[0:200]

    # item_link is only needed if NewsItem has no get_absolute_url method.
    def item_link(self, item):
        return item.url
