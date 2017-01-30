import sys
import ConfigParser
from datetime import date, timedelta

import scope.methods.semantics.preprocess as preprocess
import scope.methods.semantics.word_vector as word_vector
import scope.methods.semantics.lsi as lsi
import scope.methods.graphs.selector as selector
import scope.methods.dataprovider.provider as provider
import curate.methods.tests as tests
from scope.methods.learning import binary_classifier

from scope.models import Customer
from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer, Curate_Rejection_Reasons

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

        wv_language_dict = {
            'ger': 'de',
            'eng': 'en',
        }

        self.wv_model = word_vector.Model(wv_language_dict[self.language])

        if self.config.getint('classifier', 'pre_pipeline'):
            self.classifier = binary_classifier.binary_classifier(
                self.wv_model.pipeline, customer_key)

    def _classifier(self, db_articles):
        filtered_articles = []

        # update classifier
        self._update_classifier()


        # filtered_articles = self.classifier.classify(db_articles)
        filtered_articles = self.classifier.classify_by_count(
            db_articles, self.config.getint('classifier', 'min_count'))

        # Debug line - creates clustering csv
        # self.classifier.classify_labels(db_articles, True)

        print "Number of filtered articles"
        print len(filtered_articles)
        # for article in filtered_articles:
        #     print article.title

        return filtered_articles

    def _update_classifier(self):
        # positive articles
        time_since_last_training = date.today() - timedelta(
            days=self.config.getint('classifier', 'training_interval'))
        queries = Curate_Query.objects.filter(curate_customer= self.curate_customer).filter(
            time_stamp__gt=time_since_last_training).filter(
                selection_made=True)
        relevant_articles = Article_Curate_Query.objects.filter(
            curate_query__in=queries)
        pos = []
        for article_instance in relevant_articles:
            if article_instance.selection_options.filter(kind="sel").exists():
                pos.append(article_instance.article)
        
        #neative articles 
        content_reasons = Curate_Rejection_Reasons.objects.filter(selection.curate_customer = self.curate_customer).filter(kind="con")
        neg = content_reasons.current_members.all()

        if len(neg) > 0:
            self.classifier.update_model(neg, pos)

        content_reasons.current_members.clear()
        content_reasons.save()

    def _retrieve_from_sources(self):
        self.query = Curate_Query.objects.create(
            curate_customer=self.curate_customer)
        # Get the articles as dict
        db_articles = self.provider.collect_from_agents(
            self.curate_customer, self.query, self.language)
        words = sum([len(i.body) for i in db_articles])

        return db_articles, words

    def _retrieve_from_db(self):
        self.query = Curate_Query.objects.filter(
            curate_customer=self.curate_customer).order_by("pk").reverse()[0]
        article_query_instances = Article_Curate_Query.objects.filter(
            curate_query=self.query)
        db_articles = [i.article for i in article_query_instances]
        words = sum([len(i.body) for i in db_articles])
        return db_articles, words

    def _semantic_analysis(self, db_articles):
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

        return sim

    def _process(self, db_articles, words):

        print "Number of articles"
        print len(db_articles)

        if self.config.getint('classifier', 'pre_pipeline'):
            filtered_articles = self._classifier(db_articles)
        else:
            filtered_articles = db_articles

        if len(filtered_articles) > 0:
            sim = self._semantic_analysis(filtered_articles)

            sel = selector.Selection(filtered_articles, sim)
            size_bound = [self.config.getint('general', 'lower_bound'),
                          self.config.getint('general', 'upper_bound')]
            if self.selection_method == "by_test":
                steps = [self.config.getfloat(self.semantic_model, 'lower_step'),
                         self.config.getfloat(
                             self.semantic_model, 'upper_step'),
                         self.config.getfloat(self.semantic_model, 'step_size')]
                current_test = self.config.get('by_test', 'test')
                test = tests.Curate_Test(current_test).test
                test_params = []
                for i in self.config.options(current_test):
                    test_params.append(self.config.getfloat(current_test, i))
                params = [steps, test_params]
                selection = sel.by_test(test, params, size_bound)
            if self.selection_method == "global_thresh":
                threshold = self.config.getfloat('global_thresh', 'threshold')
                selection = sel.global_thresh(self.test, threshold, size_bound)

            previous_articles = Article_Curate_Query.objects.filter(
                curate_query__curate_customer=self.curate_customer).filter(rank__gt=0)
            selected_articles = [filtered_articles[i[0]]
                                 for i in selection['articles'] if not previous_articles.filter(article__url=filtered_articles[i[0]].url).exists()]

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
        else:
            selected_articles = []
        return selected_articles

    def from_db(self):
        db_articles, words = self._retrieve_from_db()
        selected_articles = self._process(db_articles, words)

        return selected_articles

    def from_sources(self):
        db_articles, words = self._retrieve_from_sources()
        selected_articles = self._process(db_articles, words)

        return selected_articles
