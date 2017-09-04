'''
Handles the different data providers and saves the articles.
'''

from django.core.exceptions import ValidationError

from scope.models import Source, Article
from curate.models import Curate_Retrieval, Article_Curate_Retrieval
from tldextract import tldextract
from . import imap_handler, feed_handler #, er_handler, news_handler


class Provider(object):
    """docstring for crawler."""

    def __init__(self):
        self.retrieval = Curate_Retrieval.objects.create()

    def collect_all(self, out=True):

        db_articles = []
        # newspaper_articles = []

        #first get all email data
        imap = imap_handler.ImapHandler()
        imap_out_list = imap.get_data_new()
        db_articles.extend(self._save_articles(
                imap_out_list))

        #get event registries that are subscribed
        # print("er")
        # er = er_handler.EventRegistry(con.agent_object)
        # newspaper_articles.append((er.get_data(), con))


        #get all newspaper sources that are subsribed
        # print("newspaper")
        # news = news_handler.NewsSourceHandler()
        # newspaper_articles.append((news.get_articles_from_source(
        #             con.agent_object.url, 24), con))

        # Get all sources connected to the curate_customer
        # connector = Agent.objects.filter(
        #     product_customer_id=curate_customer.id)

        #feeds
        feed = feed_handler.Feed_Handler()
        feed_out_list = feed.collect_used_feeds()
        db_articles.extend(self._save_articles(feed_out_list))
        if out==True:
            return db_articles

    def _save_articles(self, article_list):
        #the input to this is a dict for every article of the given agent format.
        db_articles = []

        print("Filter duplicates before _save_articles based on the title")
        print("Initial size")
        print(len(article_list))

        articles = []
        #this is meant to be avoiding double titles? as a hard coded check...seems less than ideal computationally
        titles = []
        for a in article_list:
            if a['title'] not in titles:
                titles.append(a['title'])
                articles.append(a)

        print("Filtered size")
        print(len(articles))

        # Save the articles into the database
        for a in articles:
            try:
                # Check if source already exists
                source, created = Source.objects.get_or_create(
                    url=a['source'],
                    defaults={"name": tldextract.extract(a['source']).domain.title()})

                # make sure that for every newsletter no duplicates are let
                # through, while allowing duplicate articles when they derive
                # from different newsletters
                art, created = Article.objects.get_or_create(
                    title=a['title'],
                    url=a['url'],
                    defaults={"source": source, "body": a['body'],
                              "images": a['images'], "pubdate": a['pubdate']})

                if 'summary' in a:
                    art.sample = a['summary']
                    art.save()

                art_cur_ret, created = Article_Curate_Retrieval.objects.get_or_create(retrieval=self.retrieval, article=art)

                if 'newsletter' in a:
                        art_cur_ret.newsletter = a['newsletter']
                        art_cur_ret.save() 
                if 'feed' in a:
                        art_cur_ret.feed = a['feed']
                        art_cur_ret.save()                

                db_articles.append(art)

            except ValidationError:
                print("Validation Error")
                continue

        return db_articles
