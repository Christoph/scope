'''
Url extraction class
'''

import re
import spacy
from urllib.parse import urlparse
import urllib.request, urllib.error, urllib.parse
from http.cookiejar import CookieJar
from scope.methods.dataprovider import constants


class Extractor(object):
    """Helper methods for the data provider module."""

    def __init__(self, nlp):
        self.nlp = nlp
        self.cj = CookieJar()
        # Some pages need cookie support.
        self.url_opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cj))
        # User-Agent let the call look like a browser call.

        headers = [
            ('User-Agent',
             'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'),
            ('Accept',
             'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
            ('Connection', 'keep-alive'),
            ('Accept-Language', 'en-US,en;q=0.8,de;q=0.6'),
            ('Accept-Encoding', 'gzip, deflate, sdch'),
            ('Upgrade-Insecure-Requests', '1'),
            ('Cache-Control', 'max-age=0')
        ]

        self.url_opener.addheaders = headers

    def get_urls_from_string(self, content):
        urls_list = []
        blacklisted = []
        bad_urls = []

        urls = re.findall(
            (r'http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[:/?#\[\]@+\-\._~=]|[!$&\'()*+,;=]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'),
            content)

        # urls = []
        text = self.nlp(content)

        for t in text:
            if t.like_url and not t.like_email:
                urls.append(t.text)

        # Get real article urls
        for url in list(set(urls)):
            try:
                if url not in bad_urls:
                    # Check url
                    res = self.url_opener.open(url)
                    finalurl = res.geturl()
                    check_url = urlparse(finalurl)

            # TODO: Shoudnt catch all exceptions
            except:
                bad_urls.append(url)
                continue

            if (check_url.path not in constants.URL_PATH_BLACKLIST and
                    check_url.hostname not in
                    constants.URL_HOSTNAME_BLACKLIST):
                urls_list.append(finalurl)
            else:
                blacklisted.append(finalurl)

        # Show all bad urls
        print(bad_urls)

        return urls_list

    def _blacklist_comparison(self, blacklist, text):
        for item in blacklist:
            if text.find(item) >= 0:
                return True
            else:
                return False
