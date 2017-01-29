'''
Handels newspaper crawling
'''

from urlparse import urlparse
from lxml.etree import XMLSyntaxError

import newspaper

from scope.models import Article


class NewsSourceHandler(object):
    """NewsPaperHandler."""

    def _download_articles(self, articles):
        for a in articles:
            try:
                a.download()
                a.parse()
            except XMLSyntaxError:
                print "Parse error detected"
                print a.url

            # Remove newline characters
            a.text = a.text.replace("\n", "")

        print "Articles downloaded and parsed"
        return articles

    def _check_urls(self, articles):
        out = []

        for a in articles:
            if Article.objects.filter(url=a.url).exists():
                print "Url already exists: " + a.url
            else:
                out.append(a)

        return out

    def get_articles_from_list(self, url_list, language):
        ''' Download and parse articles from list.'''
        articles = []

        newspaper_lang_dict = {
            'ger': 'de',
            'eng': 'en',
        }

        # Create newspaper article list
        for i in range(0, len(url_list)):
            try:
                if language == "mix":
                    articles.append(newspaper.Article(url_list[i]))
                else:
                    articles.append(newspaper.Article(
                        url_list[i],
                        language=newspaper_lang_dict[language]))
            except:
                print "Error while  converting " + url_list[i]
                continue

        # out = self._download_articles(self._check_urls(articles))
        out = self._download_articles(articles)

        return out

    def get_articles_from_source(self, url):
        ''' Download and parse articles from source.'''
        out = []

        source = newspaper.build(url, memoize_articles=False)

        try:
            articles = self._download_articles(source.articles)
        except XMLSyntaxError:
            print "Error during download"

        for article in articles:
            if len(article.text) > 0 and len(article.title) > 0:
                out.append({
                    "body": article.text, "title": article.title,
                    "url": article.url, "images": article.top_image,
                    "source": urlparse(article.url).netloc,
                    "pubdate": article.publish_date})
            else:
                print "Article not correctly parsed."

        return out