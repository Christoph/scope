from datetime import datetime, timedelta
from eventregistry import EventRegistry, QueryArticles, ArticleInfoFlags
from eventregistry import RequestArticlesInfo, ReturnInfo


class EventRegistryHandler(object):
    """docstring for ImapHandler."""
    def __init__(self, agent):
        self.lang = agent.lang.encode("utf-8")
        self.concepts = agent.concepts.encode("utf-8").split(",")
        self.locations = agent.locations.encode("utf-8").split(",")

    def get_data(self):

        out = []

        er = EventRegistry()
        er.login("christoph.kralj@gmail.com", "XzbiyLnpeh8MBtC{$4hv")

        # Create query using language
        q = QueryArticles(lang=self.lang)

        # Set search params
        q.setDateLimit(datetime.today() - timedelta(days=1), datetime.today())

        if len(self.concepts) > 1:
            for con in self.concepts:
                q.addConcept(er.getConceptUri(con))

        if len(self.locations) > 0:
            for loc in self.locations:
                q.addLocation(er.getLocationUri(loc))

        # Get the total number ob pages
        q.addRequestedResult(RequestArticlesInfo(
            count=200,
            sortBy="date"
            ))

        articles = er.execQuery(q)

        try:
            pages = articles["articles"]["pages"]
        except KeyError:
            print articles

        q.clearRequestedResults()

        # Get all articles
        for i in xrange(1, pages+1):
            q.addRequestedResult(RequestArticlesInfo(
                page=i,
                count=200,
                sortBy="date",
                returnInfo=ReturnInfo(
                    articleInfo=ArticleInfoFlags(
                        bodyLen=-1,
                        image=True))
                ))

            articles = er.execQuery(q)
            q.clearRequestedResults()

            for article in articles["articles"]["results"]:
                out.append({
                    "body": article["body"], "title": article["title"],
                    "url": article["url"], "images": article["image"],
                    "source": article["source"]["uri"],
                    "source_name": article["source"]["title"]})

        return out
