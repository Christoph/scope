import sys

import scope.methods.semantics.preprocess as preprocess
import scope.methods.semantics.word_vector as word_vector
import scope.methods.semantics.lsi as lsi
import scope.methods.graphs.selector as selector
import scope.methods.dataprovider.provider as provider

from scope.models import Article, Customer, Source
from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer

reload(sys)
sys.setdefaultencoding('utf8')


class Curate(object):
    """docstring for Graph."""

    def __init__(self, model, customer_key, test, params, size_bound, lsi_dim):
        self.provider = provider.Provider()
        self.model = model

        self.customer = Customer.objects.get(
            customer_key=customer_key)
        self.curate_customer = Curate_Customer.objects.get(
            customer=self.customer)
        self.query = Curate_Query.objects.create(
            curate_customer=self.curate_customer)

        self.test = test
        self.params = params
        self.lsi_dim = lsi_dim
        self.size_bound = size_bound

    def _retrieve_from_sources(self):

        # Get the articles as dict
        db_articles = self.provider.collect_from_agents(
            self.curate_customer, self.query)
        words = sum([len(i.body) for i in db_articles])

        return db_articles, words

    def _retrieve_from_db(self):

        article_query_instances = Article_Curate_Query.objects.filter(
            curate_query=self.query)
        db_articles = [i.article for i in article_query_instances]
        words = sum([len(i.body) for i in db_articles])
        return db_articles, words

    def _semantic_analysis(self, db_articles):
        if self.model == "lsi":
            pre = preprocess.PreProcessing("english")
            lsi_model = lsi.Model()

            vecs = pre.stemm([a.body for a in db_articles])
            lsi_model.compute(vecs, self.lsi_dim)

            sim = lsi_model.similarity()
        if self.model == "wv":
            wv_model = word_vector.Model("en")

            wv_model.load_data(db_articles)
            sim = wv_model.similarity_matrix()

        return sim

    def _process(self, db_articles, words):

        sim = self._semantic_analysis(db_articles)

        sel = selector.Selection(len(db_articles), sim)
        selection = sel.by_test(self.test, self.params, self.size_bound)
        selected_articles = [db_articles[i[0]]
                             for i in selection['articles']]

        self.query.processed_words = words
        self.query.no_clusters = selection[
            'no_clusters']
        self.query.clustering = selection['clustering']
        self.query.save()

        for i in range(0, len(selected_articles)):
            a = Article_Curate_Query.objects.get(
                article=selected_articles[i], curate_query=self.query)
            a.rank = i + 1
            a.save()
        return selected_articles

    def from_db(self):
        db_articles, words = self._retrieve_from_db()
        selected_articles = self._process(db_articles, words)

        return selected_articles

    def from_sources(self):
        db_articles, words = self._retrieve_from_sources()
        selected_articles = self._process(db_articles, words)

        return selected_articles
