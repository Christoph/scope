from django.test import TestCase
from curate.models import Article_Curate_Query, Curate_Customer, Curate_Query, Curate_Query_Cluster
from scope.models import Customer, Article, Source, Newsletter
from curate.methods import curate_process

from datetime import date
from random import randint


def create_test_customer(customer_key):
    customer = Customer(customer_key=customer_key)
    customer.save()
    curate_customer = Curate_Customer(customer=customer, expires=date.today())
    curate_customer.save()
    query = Curate_Query(curate_customer=curate_customer)
    query.save()
    return customer, curate_customer, query


def create_labels(cluster_size, articles):
    pre_labels = zip(*[iter(articles)] * cluster_size)
    out = []
    for i in pre_labels:
        i = list(i)
        out.append([i[0], i])
    return out


def create_articles(no):
    out = []
    for i in range(0, no):
        article = Article(title="Test Title" + str(i),
                          url="https://url" + str(i))
        article.save()
        out.append(article)
    return out


def create_newsletters(no):
    out = []
    for i in range(0, no):
        item = Newsletter(name="Test Newsletter" + str(i),
                          email="paul@" + str(i) + ".com")
        item.save()
        out.append(item)
    return out


def create_instances(articles, query, newsletters):
    out = []
    for article in articles:
        newsletter = newsletters[randint(0, len(newsletters) - 1)]
        instance = Article_Curate_Query(
            article=article, curate_query=query, newsletter=newsletter)
        instance.save()
        out.append(instance)
    return out


class Curate_Object_Tests(TestCase):
    """Checks the various methods of the Curate objects defined in curate_process.py"""

    def test_bad_articles_are_actually_filtered_test_by_title(self):
        customer, curate_customer, query = create_test_customer(
            "commerzbank_germany")
        cur = curate_process.Curate(customer_key="commerzbank_germany")
        article = Article(title="Test Title", url="url1")
        article.save()
        article2 = Article(title="Test Title", url="url2")
        article2.save()
        bad_article = Article_Curate_Query(
            bad_article=True, article=article, curate_query=query)
        bad_article.save()

        self.assertIs(len(cur.filter_bad_articles([article2])), 0)

    def test_bad_articles_are_actually_filtered_test_by_url(self):
        customer, curate_customer, query = create_test_customer(
            "commerzbank_germany")
        cur = curate_process.Curate(customer_key="commerzbank_germany")
        article = Article(title="Test Title1", url="url")
        article.save()
        article2 = Article(title="Test Title2", url="url")
        article2.save()
        bad_article = Article_Curate_Query(
            bad_article=True, article=article, curate_query=query)
        bad_article.save()

        self.assertIs(len(cur.filter_bad_articles([article2])), 0)

    def test_bad_sources_are_actually_filtered(self):
        customer, curate_customer, query = create_test_customer(
            "commerzbank_germany")
        cur = curate_process.Curate(customer_key="commerzbank_germany")
        source = Source(name="Bad Source")
        source.save()
        curate_customer.bad_source.add(source)
        curate_customer.save()
        article = Article(title="Test Title", url="url1", source=source)
        article.save
        self.assertIs(len(cur.filter_bad_sources([article])), 0)

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
        customer, curate_customer, query = create_test_customer(
            "commerzbank_germany")
        cur = curate_process.Curate(customer_key="commerzbank_germany")
        cur._create_query_instance(db=False)
        query = cur.query
        articles = create_articles(15)
        newsletters = create_newsletters(5)
        instances = create_instances(articles, query, newsletters)
        labels = create_labels(3, articles)
        cur.produce_and_save_clusters(labels)
        articles_dict = cur._produce_cluster_dict(labels)
        clusters = Curate_Query_Cluster.objects.filter(
            center__curate_query=query).order_by('pk')

        self.assertIn([articles_dict[i] for i in articles_dict][randint(0,3)], 
            [list(cluster.cluster_articles.all()) for cluster in clusters])
        self.assertIn(instances[0],[cluster.center for cluster in clusters])
        self.assertEqual(sorted([cluster.rank for cluster in clusters]), [1, 2, 3, 4, 5])

    def test_cluster_dict_produces_correctly(self):
        customer, curate_customer, query = create_test_customer(
            "commerzbank_germany")
        cur = curate_process.Curate(customer_key="commerzbank_germany")
        cur._create_query_instance(db=False)
        query = cur.query
        articles = create_articles(15)
        newsletters = create_newsletters(5)
        instances = create_instances(articles, query, newsletters)
        labels = create_labels(3, articles)
        articles_dict = cur._produce_cluster_dict(labels)
        self.assertIn(instances[0], articles_dict[instances[0]])
        self.assertIn(instances[-1], articles_dict[instances[12]])

    def test_remove_duplicate_articles_returns_articles(self):
    	customer, curate_customer, query = create_test_customer(
            "commerzbank_germany")
        cur = curate_process.Curate(customer_key="commerzbank_germany")
        cur._create_query_instance(db=False)
        articles = create_articles(15)
        articles2 = cur.remove_duplicate_articles_for_processing(articles)
        for article in articles2:
	        self.assertIsInstance(article,Article)

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
    	customer, curate_customer, query = create_test_customer(
            "commerzbank_germany")
        cur = curate_process.Curate(customer_key="commerzbank_germany")
        cur._create_query_instance(db=False)
        articles = create_articles(15)
        articles2 = cur._filter_articles(articles)
        for article in articles2:
	        self.assertIsInstance(article,Article)


