from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed

#from .models import Select
import string

from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer, Curate_Customer_Selection
from scope.models import Customer

from datetime import date, datetime

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

# class ExtendedRSSFeed(Rss201rev2Feed):
class ExtendedRSSFeed(Rss201rev2Feed):
    """
    Create a type of RSS feed that has content:encoded elements.
    """
    def root_attributes(self):
        attrs = super(ExtendedRSSFeed, self).root_attributes()
        # Because I'm adding a <content:encoded> field, I first need to declare
        # the content namespace. For more information on how this works, check
        # out: http://validator.w3.org/feed/docs/howto/declare_namespaces.html
        attrs['xmlns:media'] = 'http://search.yahoo.com/mrss/'
        return attrs
    
    def add_item_elements(self, handler, item):
        super(ExtendedRSSFeed, self).add_item_elements(handler, item)
        if 'media:content' in item:
            handler.addQuickElement(u"media:content", item['media:content'])
        if 'source' in item:
            handler.addQuickElement(u"source", item['source'])

        # 'content_encoded' is added to the item below, in item_extra_kwargs()
        # It's populated in item_your_custom_field(). Here we're creating
        # the <content:encoded> element and adding it to our feed xml
        # if item['media_content'] is not None:
        #     handler.addQuickElement(u'media_content', item['media_content'])



class Feed(Feed):
    feed_type = ExtendedRSSFeed
    title = "Today's NHBrief"
    link = "/nh/"
    description = "Newsletter created with the help of Scope Technology"

    def get_object(self, request, customer_key, selected_option="sel", date=None):
        return [Customer.objects.get(customer_key=customer_key), selected_option, date]

    def title(self, obj):
        return "Selected articles by " + obj[0].name

    def link(self, obj):
        return "/" + obj[0].customer_key + "/"

    def items(self, obj):
        # user_profile = UserProfile.objects.get(user=request.user)
        # customer_key == user_profile.customer.customer_key:
        # print customer_key
        # customer = Customer.objects.get(customer_key=customer_key)
        #print obj
        curate_customer = Curate_Customer.objects.get(customer=obj[0])
        if date==None:
            query = Curate_Query.objects.filter(curate_customer=curate_customer).order_by("pk").last()
        else:
            date_parsed = datetime.strptime(obj[2],'%d%m%Y').date()
            print date_parsed
            query = Curate_Query.objects.filter(curate_customer=curate_customer).filter(time_stamp=date_parsed).order_by("pk").last()
        if obj[1] == "sel":
            select_options = Curate_Customer_Selection.objects.filter(curate_customer=curate_customer).filter(type="sel").all()
        else:
            select_options = Curate_Customer_Selection.objects.filter(curate_customer=curate_customer).filter(name=obj[1]).all()
        suggestions = []
        for i in Article_Curate_Query.objects.filter(curate_query=query).all():
            for option in select_options:
                if option in i.selection_options.all():
                    suggestions.append(i.article)
        #     i in .filter(selection_options__in = select_option).order_by("rank")
        # suggestions = [i.article for i in article_query_instances]
        return suggestions
    
    def item_extra_kwargs(self, item):
        # This is probably the first place you'll add a reference to the new
        # content. Start by superclassing the method, then append your
        # extra field and call the method you'll use to populate it.
        extra = super(Feed, self).item_extra_kwargs(item)
        extra.update({'media:content': self.item_your_custom_field(item)})
        extra.update({'source': self.item_source_custom_field(item)})
        return extra

    def item_your_custom_field(self, item):
        # This is your custom method for populating the field.
        # Name it whatever you want, so long as it matches what
        # you're calling from item_extra_kwargs().
        # What you do here is entirely dependent on what your
        # system looks like. I'm using a simple queryset example,
        # but this is not to be taken literally.
        # full_text = query_obj['full_story_content']
        return item.images

    def item_source_custom_field(self, item):
        return item.source.name

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

    # def item_enclosure_url(self, item):
    #     return item.images

    # def item_content_encoded(self, item):
    #     return "test"

    # item_enclosure_mime_type = "image/jpeg"

    # def item_source(self, item):
    #     return item.source.name
