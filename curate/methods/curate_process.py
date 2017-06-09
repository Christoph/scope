import configparser
import spacy

from scope.methods.semantics import document_embedding
from scope.methods.graphs import clustering_methods
import scope.methods.dataprovider.provider as provider
from scope.methods.semantics import summarizer, keywords

from scope.models import Customer

from curate.methods.filters import filter_bad_articles, filter_bad_sources
from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer, Curate_Query_Cluster


class Curate(object):
    """Curate process class."""

    def __init__(self, customer_key):
        self.config = configparser.RawConfigParser()
        self.config.read('curate/customers/' + customer_key +
                         "/" + customer_key + '.cfg')
        self.semantic_model = self.config.get(
            'general', 'current_semantic_model')
        self.customer = Customer.objects.get(
            customer_key=customer_key)
        self.curate_customer = Curate_Customer.objects.get(
            customer=self.customer)
        self.language = self.config.get(
            'general', 'language')
        self.nlp = spacy.load(self.language)
        self.provider = provider.Provider(self.nlp)

    def _create_query_instance(self, db=False):
        if db is False:
            self.query = Curate_Query.objects.create(
                curate_customer=self.curate_customer)
        else:
            self.query = Curate_Query.objects.filter(
                curate_customer=self.curate_customer).order_by("pk").last()

    def _retrieve_from_sources(self):
        # Get the articles as dict
        db_articles = self.provider.collect_from_agents(
            self.curate_customer, self.query, self.language)

        print("Number of distinct articles retrieved")
        print(len(db_articles))

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
        print("Number of distinct articles retrieved")
        print(len(db_articles))

        self.query.processed_words = sum([len(i.body) for i in db_articles])
        self.query.articles_before_filtering = len(db_articles)
        self.query.save()
        return db_articles

    def _semantic_analysis(self, db_articles):
        if self.semantic_model == "grammar_svd":
            data_model = document_embedding.Embedding(
                self.language, self.nlp, "grammar_svd", db_articles)

            vecs = data_model.get_embedding_vectors()
            sim = data_model.get_similarity_matrix()

        return sim, vecs

    def _filter_articles(self, all_articles, db=False):
        after_bad_sources = filter_bad_sources(self.curate_customer, all_articles, db=False)
        after_bad_articles = filter_bad_articles(self.curate_customer, after_bad_sources)

        return after_bad_articles

    def _produce_cluster_dict(self, cluster_articles, selected_articles):
        articles_dict = {}
        # produce a dictionary of the clusters
        for center in selected_articles:
            cluster = cluster_articles[center]
        #for center, cluster in article_clusters:
            center_instance = Article_Curate_Query.objects.filter(
                article=center, curate_query=self.query).first()
            all_article_curate_instances = []
            for article in cluster:
                article_curate_instances = Article_Curate_Query.objects.filter(
                    article__title=article.title, curate_query=self.query)
                all_article_curate_instances.extend(article_curate_instances)
            articles_dict[center_instance] = list(set(all_article_curate_instances))
            #this output is comprised of article_curate_query instances!
        return articles_dict

    def produce_and_save_clusters(self, cluster_articles, selected_articles):
        words, alternative_keywords = self.produce_keywords_and_summaries(cluster_articles, selected_articles)
        articles_dict = self._produce_cluster_dict(cluster_articles, selected_articles)
        counter = 1

        #in case you go from db:
        old_clusters = Curate_Query_Cluster.objects.filter(center__curate_query=self.query)
        old_clusters.delete()

        for key, value in articles_dict.items():
            cluster = Curate_Query_Cluster(rank=counter, center=key, keywords= str(words[key.article]) + ',' + alternative_keywords[key.article])
            cluster.save()
            #cluster.cluster_articles.clear()
            for instance in articles_dict[key]:
                cluster.cluster_articles.add(instance)
            cluster.save()
            counter += 1
        self.query.no_clusters = counter
        self.query.save()

    def produce_keywords_and_summaries(self, cluster_articles, selected_articles):
        #this input dict consists of actual article objects
        representative_model = summarizer.Summarizer(self.language, self.nlp)

        words = representative_model.get_keywords(cluster_articles, selected_articles, 1)
        alternative_keywords = keywords.keywords_from_articles(cluster_articles, selected_articles, self.language)
        return words, alternative_keywords

    def _process(self, filtered_articles):

        # filtered_articles = remove_duplicate_articles_for_processing(filtered_articles)

        if filtered_articles:
            sim, vecs = self._semantic_analysis(filtered_articles)

            cluster_articles = clustering_methods.get_clustering(
                filtered_articles, sim, vecs, self.config.getint('general', 'upper_bound'), self.config.getint('general', 'lower_bound'))

            selected_articles = clustering_methods.get_central_articles(cluster_articles, self.config.getint('general', 'output_articles'))

            print([a.title for a in selected_articles])

        # you can generate the dict at this point actually.
            self.produce_and_save_clusters(cluster_articles, selected_articles)
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
