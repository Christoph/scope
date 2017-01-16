from django.contrib.syndication.views import Feed
from django.urls import reverse

#from .models import Select

from datetime import date, datetime
import string

from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer, Curate_Customer_Selection
from scope.models import Customer, UserProfile

def truncate_words_and_prod_sentence(s, thresh):
    split = s.split(' ')
    l = 0
    i = 0
    while l < thresh  and i<len(split):
        l = len([len(split[k]) for k in range(0,i)]) + i
        i += 1

    final = string.join([split[k] for k in range(0,i)], " ")
    final = string.join(final.split('.')[:-1], ".") + '.'
    return final


class Feed(Feed):
    title = "Today's NHBrief"
    link = "/nh/"
    description = "Newsletter created with the help of Scope Technology"

    def get_object(self, request, customer_key, selected_option="sel"):
        return [Customer.objects.get(customer_key=customer_key), selected_option]

    def title(self, obj):
        return "Selected articles by " + obj[0].name

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
        return truncate_words_and_prod_sentence(item.body, 200)

    # item_link is only needed if NewsItem has no get_absolute_url method.
    def item_link(self, item):
        return item.url

    def item_pubdate(self, item):
        # return datetime.strftime(item.pubdate.replace(tzinfo=None),'%a %x %H:%M')
        return item.pubdate

    def item_enclosure_url(self, item):
        return item.images

    item_enclosure_mime_type = "jpeg"

    def item_author_name(self, item):
        return item.source.name
