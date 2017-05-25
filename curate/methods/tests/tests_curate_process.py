from django.test import TestCase
from curate.models import Curate_Query_Cluster
from scope.models import Article
from curate.methods import curate_process

from random import randint

import scope.methods.tests.testutils as testutils

class Curate_Object_Tests(TestCase):
    """Checks the various methods of the Curate objects defined in curate_process.py"""

    def test_cluster_labels_are_stored_correctly(self):
        pass

    def test_the_right_number_of_clusters_are_produced(self):
        pass

    def test_duplicate_articles_are_captured_cluster(self):
        pass

    def test_duplicate_articles_are_not_processed_into_semantic_analysis(self):
        pass

    def test_duplicate_articles_are_included_in_sem_ana_only_if_from_independent_sources(self):
        pass

    def test_clusters_are_produced_correctly(self):
        customer, curate_customer, query = testutils.create_test_customer(
            "commerzbank_germany")
        cur = curate_process.Curate(customer_key="commerzbank_germany")
        cur._create_query_instance(db=False)
        query = cur.query
        articles = testutils.create_articles(15)
        newsletters =  testutils.create_newsletters(5)
        instances =  testutils.create_instances(articles, query, newsletters)
        labels =  testutils.create_labels(3, articles)
        cur.produce_and_save_clusters(labels)
        articles_dict = cur._produce_cluster_dict(labels)
        clusters = Curate_Query_Cluster.objects.filter(
            center__curate_query=query).order_by('pk')

        self.assertIn([articles_dict[i] for i in articles_dict][randint(0,3)], 
            [list(cluster.cluster_articles.all()) for cluster in clusters])
        self.assertIn(instances[0],[cluster.center for cluster in clusters])
        self.assertEqual(sorted([cluster.rank for cluster in clusters]), [1, 2, 3, 4, 5])

    def test_cluster_dict_produces_correctly(self):
        customer, curate_customer, query =  testutils.create_test_customer(
            "commerzbank_germany")
        cur = curate_process.Curate(customer_key="commerzbank_germany")
        cur._create_query_instance(db=False)
        query = cur.query
        articles =  testutils.create_articles(15)
        newsletters =  testutils.create_newsletters(5)
        instances =  testutils.create_instances(articles, query, newsletters)
        labels =  testutils.create_labels(3, articles)
        articles_dict = cur._produce_cluster_dict(labels)
        self.assertIn(instances[0], articles_dict[instances[0]])
        self.assertIn(instances[-1], articles_dict[instances[12]])

    # def test_remove_duplicate_articles_returns_articles(self):
    # 	customer, curate_customer, query = create_test_customer(
    #         "commerzbank_germany")
    #     cur = curate_process.Curate(customer_key="commerzbank_germany")
    #     cur._create_query_instance(db=False)
    #     articles = create_articles(15)
    #     articles2 = cur.remove_duplicate_articles_for_processing(articles)
    #     for article in articles2:
	   #      self.assertIsInstance(article,Article)

    # def test_classifier_method_returns_articles(self):
    # 	customer, curate_customer, query = create_test_customer(
    #         "commerzbank_germany")
    #     cur = curate_process.Curate(customer_key="commerzbank_germany")
    #     cur._create_query_instance(db=False)
    #     articles = create_articles(15)
    #     articles2 = cur._classifier(articles)
    #     for article in articles2:
	   #      self.assertIsInstance(article,Article)


    # def test_process_method_returns_articles(self):
    # 	customer, curate_customer, query = create_test_customer(
    #         "commerzbank_germany")
    #     cur = curate_process.Curate(customer_key="commerzbank_germany")
    #     cur._create_query_instance(db=False)
    #     articles = create_articles(15)
    #     articles2 = cur._process(articles)
    #     for article in articles2:
	   #      self.assertIsInstance(article,Article)

    def test_filter_articles_method_returns_articles(self):
    	customer, curate_customer, query =  testutils.create_test_customer(
            "commerzbank_germany")
        cur = curate_process.Curate(customer_key="commerzbank_germany")
        cur._create_query_instance(db=False)
        articles =  testutils.create_articles(15)
        articles2 = cur._filter_articles(articles)
        for article in articles2:
	        self.assertIsInstance(article,Article)


