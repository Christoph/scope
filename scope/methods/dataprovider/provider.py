from scope.models import AgentImap, Agent, Source, Article, AgentEventRegistry
from curate.models import Article_Curate_Query
from tldextract import tldextract

from . import imap_handler, er_handler


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

        return db_articles

    def _save_articles(self, articles, curate_query, agent):
        db_articles = []

        # Save the articles into the database
        for a in articles:
            # Check if source already exists
            source, created = Source.objects.get_or_create(
                url=a['source'], 
                defaults={"name": tldextract.extract(a['source']).domain.title()})

            art, created = Article.objects.get_or_create(
                title=a['title'],
                url=a['url'],
                defaults={"source": source, "body": a['body'],
                          "images": a['images'], "pubdate": a['pubdate']})

            Article_Curate_Query.objects.create(
                article=art, curate_query=curate_query, agent=agent)

            db_articles.append(art)

        return db_articles
