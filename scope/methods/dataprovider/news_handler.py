'''
Handels newspaper crawling
'''

from datetime import datetime, timedelta
from urllib.parse import urlparse
from lxml import etree

import newspaper

from scope.models import Article

class ScopeNewspaperArticle(newspaper.Article):

    def __eq__(self, other):
        return self.title==other.title
    def __hash__(self):
        return hash(('title', self.title))

class NewsSourceHandler(object):
    """NewsPaperHandler."""

    def _download_articles(self, articles):
        for a in articles:
            try:
                a.download()
                a.parse()
            except etree.XMLSyntaxError:
                print("Parse error detected")
                # print a.url
            except ValueError:
                print("Value error detected")
                # print a.url
            except etree.ArticleException:
                print("Value error detected")
                # print a.url

            # Remove newline characters
            a.text = a.text.replace("\n", " ")

        print("Articles downloaded and parsed")
        return articles

    # def _check_urls(self, articles):
    #     out = []

    #     for a in articles:
    #         if Article.objects.filter(url=a.url).exists():
    #             print "Url already exists"
    #             # print a.url
    #         else:
    #             out.append(a)

    #     return out

    def get_articles_from_list(self, article_dict, language):
        ''' Download and parse articles from list.'''
        out = []
        newspaper_lang_dict = {
            'ger': 'de',
            'eng': 'en',
        }

        # Create newspaper article list
        for articles, agent in article_dict:
            article_list = []
            for i in range(0,len(articles)):
                try:
                    if language == "mix":
                        article_list.append(ScopeNewspaperArticle(articles[i]))
                    else:
                        article_list.append(ScopeNewspaperArticle(
                            articles[i],
                            language=newspaper_lang_dict[language]))
                except:
                    print("Error while  converting " + articles[i])
                    continue

            out.append([self._download_articles(article_list), agent])

        # out = self._download_articles(self._check_urls(articles))

        return out

    def get_articles_from_source(self, url, timespan):
        ''' Download and parse articles from source.'''
        out = []
        old = datetime.now() - timedelta(hours=timespan)

        source = newspaper.build(url, memoize_articles=False)

        try:
            articles = self._download_articles(source.articles)
        except etree.XMLSyntaxError:
            print("Error during download")

        for article in articles:
            if len(article.text) > 0 and len(article.title) > 0 and article.publish_date is not None:

                if article.publish_date > old:
                    out.append({
                        "body": article.text, "title": article.title,
                        "url": article.url, "images": article.top_image,
                        "source": urlparse(article.url).netloc,
                        "pubdate": article.publish_date})
                # else:
                #     print "Article is too old"
                #     print article.publish_date
            # else:
            #     print "Article not correctly parsed."

        return out

    def produce_output_dict(self, article_dict):
        out = []
        for articles, newsletter in article_dict:
            out.extend([{
                        "body": article.text, "title": article.title,
                        "url": article.url, "images": article.top_image,
                        "source": urlparse(article.url).netloc,
                        "pubdate": article.publish_date,
                        "newsletter": newsletter} for article in articles])
        return out
