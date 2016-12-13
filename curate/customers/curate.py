import sys
from datetime import date
# from curate.models import Select

import scope.methods.semantics.preprocess as preprocess
import scope.methods.semantics.word_vector as word_vector
import scope.methods.graphs.selector as selector
import scope.methods.dataprovider.provider as provider

from scope.models import Article, Customer, Source
from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer

reload(sys)
sys.setdefaultencoding('utf8')


class Curate():
    """docstring for Graph."""

    def __init__(self, type, customer_key, test, params, size_bound):
        if type is "new":
            self.query = Curate_Query.objects.create(curate_customer=curate_customer)
        elif type is "last":
        	self.time = date.today() # TODO needs to become a "NONE"
        	self.query = Curate_Query.objects.filter(
		        curate_customer=self.curate_customer).filter(time_stamp = self.time).order_by("time_stamp")[0]

        self.customer = Customer.objects.get(customer_key=customer_key)
        self.curate_customer = Curate_Customer.objects.get(customer=customer)
        self.test = test
        self.params = params
        self.size_bound = size_bound

    def _retrieve_from_sources(self):

    	# Get all sources connected to the curate_customer
		source = Source.objects.get(
		    product_customer_id=self.curate_customer.id)

		agent = source.agent_object
        data_provider = provider.Provider()
                # Get the articles as dict
        data = data_provider.query_source(agent)
        db_articles = []
		words = 0

        for a in data:
		    art, created = Article.objects.get_or_create(
		        source=source,
		        title=a['title'],
		        url=a['url'],
		        body=a['body'],
		        images=a['images'])

	        Article_Curate_Query.objects.get_or_create(
	            article=art, curate_query=curate_query)
				db_articles.append(art)

		words = sum([len(i.body) for i in db_articles])

		return db_articles, words

    def _retrieve_from_db(self):

		article_query_instances = Article_Curate_Query.objects.filter(
		        curate_query= self.query)
		db_articles = [i.article for i in article_query_instances]
		words = sum([len(i.body) for i in db_articles])
		return db_articles, words

    def _process(self, db_articles, words):

    	pre = preprocess.PreProcessing("english")
		wv_model = word_vector.Model("en")
		wv_model.load_data(db_articles)
		sim = wv_model.similarity_matrix()
		sel = selector.Selection(len(db_articles), sim)
		selection = sel.by_test(self.test, self.params, self.size_bound)
		selected_articles = [db_articles[i[0]] for i in selection['articles']]

		self.query.processed_words = words
		self.query.no_clusters = selection[
                    'no_clusters']
		self.query.clustering = selection['clustering']
		self.query.save()

		for i in range(0, len(selected_articles)):
		    a = Article_Curate_Query.objects.get(article=selected_articles[i])
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
