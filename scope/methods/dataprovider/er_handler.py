'''
Handels Event Registry API
'''

from datetime import datetime, timedelta
from eventregistry import EventRegistry, QueryArticles, ArticleInfoFlags
from eventregistry import RequestArticlesInfo, ReturnInfo


class EventRegistryHandler(object):
    """docstring for ImapHandler."""
    def __init__(self, agent):
        self.user = agent.user.encode("utf-8")
        self.pwd = agent.pwd.encode("utf-8")
        self.lang = agent.lang.encode("utf-8")
        self.concepts = agent.concepts.encode("utf-8").split(",")

        if len(agent.locations.encode("utf-8")) > 0:
            self.locations = agent.locations.encode("utf-8").split(",")
        else:
            self.locations = []

    def get_data_with_checks(self, timespan, number, blacklist, text_min_length):
        '''
        Get data with the agent configuration.

        timespan[int]: How many days into the past
        number[int]: Number of articles to retrieve. Defaults to all
        '''

        out = []
        pages = 0

        er = EventRegistry()
        er.login(self.user, self.pwd)

        # Create query using language
        q = QueryArticles(lang=self.lang)

        # Set search params
        q.setDateLimit(
            datetime.today() - timedelta(days=timespan), datetime.today())

        if len(self.concepts) > 1:
            for con in self.concepts:
                print con
                q.addConcept(er.getConceptUri(con))

        if len(self.locations) > 0:
            print self.locations
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
            print "Key Error"
            print articles

        q.clearRequestedResults()

        print "Rough article count"
        print 200 * pages

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
                if article["title"] not in blacklist and len(article["body"].replace("\n", " ")) > text_min_length and article["body"].count("traditionalRegistration") < 1:
                    out.append({
                        "body": article["body"].replace("\n", " "), "title": article["title"],
                        "url": article["url"], "images": article["image"],
                        "source": article["source"]["uri"],
                        "source_name": article["source"]["title"]})
                else:
                    print "blacklisted or bad: " + article["title"]

            print "Good articles"
            print len(out)

            if len(out) > number:
                out = out[0:number]

                return out

        return out

    def get_data(self, timespan, number):
        '''
        Get data with the agent configuration.

        timespan[int]: How many days into the past
        number[int]: Number of articles to retrieve. Defaults to all
        '''

        out = []
        pages = 0

        er = EventRegistry()
        er.login(self.user, self.pwd)

        # Create query using language
        q = QueryArticles(lang=self.lang)

        # Set search params
        q.setDateLimit(
            datetime.today() - timedelta(days=timespan), datetime.today())

        if len(self.concepts) > 1:
            for con in self.concepts:
                print con
                q.addConcept(er.getConceptUri(con))

        if len(self.locations) > 0:
            print self.locations
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
            print "Key Error"
            print articles

        q.clearRequestedResults()

        print "Rough article count"
        print 200 * pages

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
                    "body": article["body"].replace("\n", ""), "title": article["title"],
                    "url": article["url"], "images": article["image"],
                    "source": article["source"]["uri"],
                    "source_name": article["source"]["title"]})

            if len(out) > number:
                out = out[0:number]

                return out

        return out
