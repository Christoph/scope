'''
Handles the different data providers and saves the articles.
'''

from django.core.exceptions import ValidationError

from scope.models import AgentImap, Agent, Source, Article, AgentEventRegistry
from scope.models import AgentNewspaper
from curate.models import Article_Curate_Query
from tldextract import tldextract

from . import imap_handler, er_handler, news_handler


class Provider(object):
    """docstring for crawler."""

    def collect_from_agents(self, curate_customer, curate_query, language):
        db_articles = []

        # Get all sources connected to the curate_customer
        connector = Agent.objects.filter(
            product_customer_id=curate_customer.id)

        for con in connector:
            print "============= New Agent ==============="
            if isinstance(con.agent_object, AgentImap):
                print "imap"
                imap = imap_handler.ImapHandler(con.agent_object, language)

                db_articles.extend(self._save_articles(
                    imap.get_data_new(), curate_query, con))
            if isinstance(con.agent_object, AgentEventRegistry):
                print "er"
                er = er_handler.EventRegistry(con.agent_object)

                db_articles.extend(self._save_articles(
                    er.get_data(), curate_query, con))
            if isinstance(con.agent_object, AgentNewspaper):
                print "newspaper"
                news = news_handler.NewsSourceHandler()

                db_articles.extend(self._save_articles(
                    news.get_articles_from_source(
                        con.agent_object.url, 24), curate_query, con))

        return db_articles

    def _save_articles(self, articles, curate_query, agent):
        db_articles = []

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

                if
                art_cur_que = Article_Curate_Query.objects.create(
                    article=art, curate_query=curate_query, agent=agent)

                if a.has_key('newsletter'):
                    art_cur_que.newsletter = a['newsletter']
                    art_cur_que.save()

                db_articles.append(art)

            except ValidationError:
                print "Validation Error"
                continue

        return db_articles
