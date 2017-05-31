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

    def __init__(self, nlp):
        self.nlp = nlp

    def collect_from_agents(self, curate_customer, curate_query, language):
        db_articles = []

        # Get all sources connected to the curate_customer
        connector = Agent.objects.filter(
            product_customer_id=curate_customer.id)

        for con in connector:
            print("============= New Agent ===============")
            if isinstance(con.agent_object, AgentImap):
                print("imap")
                imap = imap_handler.ImapHandler(con.agent_object, language, self.nlp)

                db_articles.extend(self._save_articles(
                    imap.get_data_new(), curate_query, con))
            if isinstance(con.agent_object, AgentEventRegistry):
                print("er")
                er = er_handler.EventRegistry(con.agent_object)

                db_articles.extend(self._save_articles(
                    er.get_data(), curate_query, con))
            if isinstance(con.agent_object, AgentNewspaper):
                print("newspaper")
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

                art_cur_que, art_cur_created = Article_Curate_Query.objects.get_or_create(
                    article=art, curate_query=curate_query, agent=agent)

                if 'newsletter' in a:
                    art_cur_que.newsletter = a['newsletter']
                    art_cur_que.save()

                # This is another instance to try and get rid of overcounting
                # articles from the same agent/newsletter. Note that this does
                # not have the problem of list(set(db_articles)) below
                if art_cur_created:
                    db_articles.append(art)

            # one could also call list(set(db_articles)) here but this would
            # mean that we do not take into account the fact that the same
            # article has been posted by two independent agents/newsletters,
            # which however *should* double the weight that is given to this
            # article
            except ValidationError:
                print("Validation Error")
                continue

        return db_articles
