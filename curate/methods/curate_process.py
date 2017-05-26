import sys
import ConfigParser
import numpy as np
from datetime import date, timedelta

from scope.methods.semantics import document_embedding
from scope.methods.graphs import clustering_methods

import scope.methods.semantics.preprocess as preprocess
import scope.methods.semantics.word_vector as word_vector
import scope.methods.semantics.lsi as lsi
import scope.methods.graphs.selector as selector
import scope.methods.dataprovider.provider as provider
import curate.methods.seman_tests as tests
from scope.methods.learning import binary_classifier
from curate.methods.filters import filter_bad_articles, filter_bad_sources
# from scope.methods.filters import remove_duplicate_articles_for_processing

from scope.models import Customer
from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer, Curate_Rejection_Reasons, Curate_Query_Cluster

reload(sys)
sys.setdefaultencoding('utf8')


class Curate(object):
    """docstring for Graph."""

    def __init__(self, customer_key):
        self.config = ConfigParser.RawConfigParser()
        self.config.read('curate/customers/' + customer_key +
                         "/" + customer_key + '.cfg')
        self.provider = provider.Provider()
        self.semantic_model = self.config.get(
            'general', 'current_semantic_model')
        self.selection_method = self.config.get(
            'general', 'current_selection_method')
        self.customer = Customer.objects.get(
            customer_key=customer_key)
        self.curate_customer = Curate_Customer.objects.get(
            customer=self.customer)
        self.language = self.config.get(
            'general', 'language')


    def _classifier(self, db_articles):
        filtered_articles = []

        # update classifier
        self._update_classifier()

        # filtered_articles = self.classifier.classify(db_articles)
        filtered_articles = self.classifier.classify_by_count(
            db_articles, self.config.getint('classifier', 'min_count'))

        # Debug line - creates clustering csv
        # self.classifier.classify_labels(db_articles, True)

        print "Number of articles after classification"
        print len(filtered_articles)
        for article in filtered_articles:
            print article.title

        return filtered_articles

    def _update_classifier(self):
        # positive articles
        time_since_last_training = date.today() - timedelta(
            days=self.config.getint('classifier', 'training_interval'))
        queries = Curate_Query.objects.filter(curate_customer=self.curate_customer).filter(
            time_stamp__gt=time_since_last_training).filter(
                selection_made=True)
        relevant_articles = Article_Curate_Query.objects.filter(
            curate_query__in=queries)
        pos = []
        neg = []
        for article_instance in relevant_articles:
            if article_instance.selection_options.filter(kind="sel").exists():
                pos.append(article_instance.article)

        content_reasons = Curate_Rejection_Reasons.objects.filter(
            selection__curate_customer=self.curate_customer).filter(kind="con")
        for reason in content_reasons:
            neg.extend(reason.current_members.all())
            reason.current_members.clear()
            reason.save()

        if len(neg) > 0:
            self.classifier.update_model(neg, pos)


    def _create_query_instance(self, db=False):
        if db == False:
            self.query = Curate_Query.objects.create(
            curate_customer=self.curate_customer)
        else:
            self.query = Curate_Query.objects.filter(
            curate_customer=self.curate_customer).order_by("pk").last()

    def _retrieve_from_sources(self):
        # Get the articles as dict
        db_articles = self.provider.collect_from_agents(
            self.curate_customer, self.query, self.language)

        print "Number of distinct articles retrieved"
        print len(db_articles)

        self.query.processed_words = sum([len(i.body) for i in db_articles])
        self.query.articles_before_filtering = len(db_articles)
        self.query.save()


        return db_articles

    def _retrieve_from_db(self):
        article_query_instances = Article_Curate_Query.objects.filter(
            curate_query=self.query)
        for i in article_query_instances:
            i.rank = 0
            i.save()
        db_articles = [i.article for i in article_query_instances]
        print "Number of distinct articles retrieved"
        print len(db_articles)

        self.query.processed_words = sum([len(i.body) for i in db_articles])
        self.query.articles_before_filtering = len(db_articles)
        self.query.save()
        return db_articles

    def _semantic_analysis(self, db_articles):
        wv_language_dict = {
            'ger': 'de',
            'eng': 'en',
        }

        self.wv_model = word_vector.Model(wv_language_dict[self.language])

        if self.config.getint('classifier', 'pre_pipeline'):
            self.classifier = binary_classifier.binary_classifier(
                self.wv_model.pipeline, self.customer.customer_key)

        if self.semantic_model == "lsi":
            lsi_language_dict = {
                'ger': 'german',
                'eng': 'english',
            }
            pre = preprocess.PreProcessing(lsi_language_dict[self.language])
            lsi_model = lsi.Model()
            lsi_dim = self.config.getint('lsi', 'lsi_dim')

            vecs = pre.stemm([a.body for a in db_articles])
            lsi_model.compute(vecs, lsi_dim)

            sim = lsi_model.similarity()

        if self.semantic_model == "wv":

            self.wv_model.load_data(db_articles)
            sim = self.wv_model.similarity_matrix()
            vecs = self.wv_model.document_vectors()

        if self.semantic_model == "grammar_svd":
            language_dict = {
                'ger': 'de',
                'eng': 'en',
            }
            data_model = document_embedding.Embedding(
                language_dict[self.language], "grammar_svd", db_articles)

            vecs = data_model.get_embedding_vectors()
            sim = data_model.get_similarity_matrix()

        return sim, vecs

    def _filter_articles(self, all_articles, db=False):
        after_bad_sources = filter_bad_sources(self.curate_customer, all_articles, db=False)
        after_bad_articles = filter_bad_articles(self.curate_customer, after_bad_sources)

        return after_bad_articles

    def _produce_cluster_dict(self, labels):
        articles_dict = {}
        #produce a dictionary of the clusters
        for center, cluster in labels:
            center_instance = Article_Curate_Query.objects.filter(
                    article=center, curate_query=self.query).first()
            all_article_curate_instances = []
            for article in cluster:
                article_curate_instances = Article_Curate_Query.objects.filter(
                    article__title=article.title, curate_query=self.query)
                all_article_curate_instances.extend(article_curate_instances)
            articles_dict[center_instance] = list(set(all_article_curate_instances))
        return articles_dict

    def produce_and_save_clusters(self,labels):
        articles_dict = self._produce_cluster_dict(labels)
        counter = 1
        for key in articles_dict:
            cluster = Curate_Query_Cluster(rank=counter, center=key)
            cluster.save()
            for instance in articles_dict[key]:
                cluster.cluster_articles.add(instance)
            cluster.save()
            counter += 1
        self.query.no_clusters = counter
        self.query.save()

    def _process(self, db_articles):

        if self.config.getint('classifier', 'pre_pipeline'):
            filtered_articles = self._classifier(db_articles)
        else:
            filtered_articles = db_articles

        # filtered_articles = remove_duplicate_articles_for_processing(filtered_articles)

        if len(filtered_articles) > 0:
            sim, vecs = self._semantic_analysis(filtered_articles)

            # sel = selector.Selection(filtered_articles, sim)
            # size_bound = [self.config.getint('general', 'lower_bound'),
            #               self.config.getint('general', 'upper_bound')]
            # if self.selection_method == "by_test":
            #     steps = [self.config.getfloat(self.semantic_model, 'lower_step'),
            #              self.config.getfloat(
            #                  self.semantic_model, 'upper_step'),
            #              self.config.getfloat(self.semantic_model, 'step_size')]
            #     current_test = self.config.get('by_test', 'test')
            #     test = tests.Curate_Test(current_test).test
            #     test_params = []
            #     for i in self.config.options(current_test):
            #         test_params.append(self.config.getfloat(current_test, i))
            #     if current_test == "clusters":
            #         if len(filtered_articles) <= 2 * self.config.getfloat(current_test, 'upper_cluster_bound'):
            #             size_bound[0] = 1
            #
            #     params = [steps, test_params]
            #     selection = sel.by_test(test, params, size_bound)
            #
            #     selected_articles = [filtered_articles[i[0]]
            #                          for i in selection['articles']]

            # self.query.no_clusters = selection[
            # 'no_clusters']
            # self.query.clustering = selection['clustering']

            selected_articles, cluster_articles = clustering_methods.get_clustering(filtered_articles, sim, vecs, self.config.getint('general', 'upper_bound'))

            # previous_articles = Article_Curate_Query.objects.filter(
            #     curate_query__curate_customer=self.curate_customer).filter(rank__gt=0)
            # selected_articles = [filtered_articles[i[0]]
            #                      for i in selection['articles']]

            # you can generate the dict at this point actually.
            self.produce_and_save_clusters(cluster_articles)

            # for i in range(0, len(selected_articles)):
            #     a = Article_Curate_Query.objects.filter(
            #         article=selected_articles[i], curate_query=self.query)[0]
            #     a.rank = i + 1
            #     a.save()
        else:
            selected_articles = []
        return selected_articles

    def from_db(self):
        self._create_query_instance(db=True)
        db_articles = self._retrieve_from_db()
        db_articles = self._filter_articles(db_articles, db=True)
        selected_articles = self._process(db_articles)

        return selected_articles

    def from_sources(self):
        self._create_query_instance(db=False)
        db_articles = self._retrieve_from_sources()
        db_articles = self._filter_articles(db_articles)
        selected_articles = self._process(db_articles)

        return selected_articles
