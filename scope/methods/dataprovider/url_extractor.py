import re
from urlparse import urlparse
import urllib2
from cookielib import CookieJar


class Extractor(object):
    """Helper methods for the data provider module."""
    def __init__(self):
        self.cj = CookieJar()
        # Some pages need cookie support.
        self.url_opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self.cj))
        # User-Agent let the call look like a browser call.
        self.url_opener.addheaders = [
            ('User-Agent',
             ('Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127',
              'Firefox/2.0.0.11'))]

    def get_urls_from_string(self, content):
        test_list = []
        urls_list = []

        # list set to remove duplicates
        # Still problems with links like:
        # http://www.cinemablend.com/news/1595010/why-jason-momoa-relates-so-closely-to-aquaman
        urls = set(list(re.findall(
            (r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|'
             '(?:%[0-9a-fA-F][0-9a-fA-F]))+'),
            content)))

        # Get real article urls
        for url in urls:
            try:
                url = url.rstrip(')')
                # req = urllib2.Request(url)
                # res = urllib2.urlopen(req)
                res = self.url_opener.open(url)
                finalurl = res.geturl()
                check_url = urlparse(finalurl)
            # TODO: Shoudnt catch all exceptions
            except:
                print "error while checking url: " + url
                continue

            # TODO: Not sure what is the use of this lines
            # Maybe creating a blacklist and not a whitelist?
            # for x in constants.SUBSCRIBED_URLS:
            #     if x in finalurl:
            #         test_list.append("yes")
            #     else:
            #         print "Not taken in first test: " + finalurl

            # if len(test_list) == 0 and (check_url.path != '/' and
            #                             check_url.path != '' and
            #                             check_url.path != '/en/'):
            #     urls_list.append(finalurl)
            # else:
            #     print "Not taken in second test: " + finalurl

            if len(check_url.path) > 1 and check_url.path != "/unsupported-browser":
                urls_list.append(finalurl)
            else:
                print "Bad url: " + finalurl

            # urls_list.append(finalurl)

        return urls_list
