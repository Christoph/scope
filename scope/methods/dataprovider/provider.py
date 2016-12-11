from scope.models import AgentImap, Agent, Source, Article
from curate.models import Article_Curate_Query

from . import imap_handler


class Provider(object):
    """docstring for crawler."""

    def __init__(self):
        self.imap = imap_handler.ImapHandler()

    def collect_from_agents(self, curate_customer, curate_query):
        db_articles = []
        agents = []

        # Get all sources connected to the curate_customer
        connector = Agent.objects.filter(
            product_customer_id=curate_customer.id)

        for con in connector:
            agents.append(con.agent_object)

        for agent in agents:
            if isinstance(agent, AgentImap):
                db_articles.extend(self._save_articles(
                    self.imap.get_data(agent), curate_query))

        return db_articles

    def _save_articles(self, articles, curate_query):
        db_articles = []

        # Save the articles into the database
        for a in articles:
            # Check if source already exists
            source, created = Source.objects.get_or_create(url=a['source'])

            art, created = Article.objects.get_or_create(
                title=a['title'],
                url=a['url'],
                defaults={"source": source, "body": a['body'],
                          "images": a['images'],
                          "description": a['description']})

            Article_Curate_Query.objects.get_or_create(
                article=art, curate_query=curate_query)

            db_articles.append(art)

        return db_articles
