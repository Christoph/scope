from django.contrib.syndication.views import Feed
from django.urls import reverse

#from .models import Select

from datetime import date

from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer, Curate_Customer_Selection
from scope.models import Customer, UserProfile


class Feed(Feed):
    title = "Today's NHBrief"
    link = "/nh/"
    description = "Newsletter created with the help of Scope Technology"

    def get_object(self, request, customer_key, selected_option="sel"):
        return [Customer.objects.get(customer_key=customer_key), selected_option]

    def title(self, obj):
        return "Selected articles by" + obj[0].name

    def link(self, obj):
        return "/" + obj[0].customer_key + "/"

    def items(self, obj):
        # user_profile = UserProfile.objects.get(user=request.user)
        # customer_key == user_profile.customer.customer_key:
        # print customer_key
        # customer = Customer.objects.get(customer_key=customer_key)
        print obj
        curate_customer = Curate_Customer.objects.get(customer=obj[0])
        last_query = Curate_Query.objects.filter(curate_customer=curate_customer).order_by("pk").last()
        if obj[1] == "sel":
            select_options = Curate_Customer_Selection.objects.filter(curate_customer=curate_customer).filter(type="sel").all()
        else:
            select_options = Curate_Customer_Selection.objects.filter(curate_customer=curate_customer).filter(name=obj[1]).all()
        suggestions = []
        for i in Article_Curate_Query.objects.filter(curate_query=last_query).all():
            for option in select_options:
                if option in i.selection_options.all():
                    suggestions.append(i.article)
        #     i in .filter(selection_options__in = select_option).order_by("rank")
        # suggestions = [i.article for i in article_query_instances]
        return suggestions

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.body[0:200]

    # item_link is only needed if NewsItem has no get_absolute_url method.
    def item_link(self, item):
        return item.url
