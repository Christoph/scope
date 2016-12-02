from django.contrib.syndication.views import Feed
from django.urls import reverse
#from .models import Select

from datetime import date

class Feed(Feed):
    title = "Today's NHBrief"
    link = "/nh/"
    description = "Daily neulandherzer newsletter"

    def items(self):
        return Select_NH.objects.filter(timestamp = date.today()).filter(is_selected=True).order_by('rank')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.summary

    # item_link is only needed if NewsItem has no get_absolute_url method.
    def item_link(self, item):
        return item.url