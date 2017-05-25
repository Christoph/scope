from django.test import TestCase
from curate.models import Article_Curate_Query
from scope.models import Article, Source
import curate.methods.filters as filters

import scope.methods.tests.testutils as testutils

class Curate_Filters_Tests(TestCase):
    """Checks the various methods of the Curate objects defined in curate_process.py"""

    def test_bad_articles_are_actually_filtered_test_by_title(self):
        customer, curate_customer, query = testutils.create_test_customer(
            "commerzbank_germany")
        article = Article(title="Test Title", url="url1")
        article.save()
        article2 = Article(title="Test Title", url="url2")
        article2.save()
        bad_article = Article_Curate_Query(
            bad_article=True, article=article, curate_query=query)
        bad_article.save()
        self.assertIs(len(filters.filter_bad_articles(curate_customer,[article2])), 0)

    def test_bad_articles_are_actually_filtered_test_by_url(self):
        customer, curate_customer, query = testutils.create_test_customer(
            "commerzbank_germany")
        article = Article(title="Test Title1", url="url")
        article.save()
        article2 = Article(title="Test Title2", url="url")
        article2.save()
        bad_article = Article_Curate_Query(
            bad_article=True, article=article, curate_query=query)
        bad_article.save()

        self.assertIs(len(filters.filter_bad_articles(curate_customer,[article2])), 0)

    def test_bad_sources_are_actually_filtered(self):
        customer, curate_customer, query = testutils.create_test_customer(
            "commerzbank_germany")
        source = Source(name="Bad Source")
        source.save()
        curate_customer.bad_source.add(source)
        curate_customer.save()
        article = Article(title="Test Title", url="url1", source=source)
        article.save
        self.assertIs(len(filters.filter_bad_sources(curate_customer,[article])), 0)


