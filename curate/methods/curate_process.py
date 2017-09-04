import configparser
from langdetect import detect
from datetime import datetime
import spacy

from scope.methods.semantics import document_embedding
from scope.methods.graphs import clustering_methods
from scope.methods.semantics import summarizer

from scope.models import Customer, Article

from curate.methods.filters import filter_bad_articles, filter_bad_sources
from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer, Curate_Query_Cluster, Curate_Retrieval, Article_Curate_Retrieval

#this class creates the selection for a given customer from the data retrievals in a given interval
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

    def curate(self, db):
        self._create_query_instance(db)
        articles = self._retrieve(db)
        articles = self._filter_articles(articles, db)
        cluster_articles, selected_articles = self._process(articles)
        self._produce_and_save_clusters(cluster_articles, selected_articles)
        return selected_articles

    def _create_query_instance(self, db=False):
        if not db:
            self.query = Curate_Query.objects.create(
                curate_customer=self.curate_customer)
        else:
            self.query = Curate_Query.objects.filter(
                curate_customer=self.curate_customer).order_by("pk").last()

    def _retrieve(self, db=False):
        if not db:
            now = datetime.now()
            since = now - self.curate_customer.interval
            retrievals = Curate_Retrieval.objects.filter(time_stamp__gt = since)
            article_retrieval_instances = Article_Curate_Retrieval.objects.filter(
                retrieval__in=retrievals)

            incl_newsletters = article_retrieval_instances.filter(newsletter__in = self.curate_customer.newsletters.all())
            incl_feeds = article_retrieval_instances.filter(feed__in = self.curate_customer.feeds.all())
            incl_newsletters.union(incl_feeds)

            for i in incl_newsletters:
                aci = Article_Curate_Query(article=i.article, rank=0,newsletter=i.newsletter, feed=i.feed, curate_query=self.query)
                aci.save()
            db_articles = [i.article for i in incl_newsletters]
            print("Number of distinct articles retrieved for this curate query")
            print(len(db_articles))

            self.query.processed_words = sum([len(i.body) for i in db_articles])
            self.query.articles_before_filtering = len(db_articles)
            self.query.save()
        else:
            db_articles = Article.objects.filter(article_curate_query__curate_query=self.query).distinct()
        return db_articles

    def _semantic_analysis(self, db_articles):
        if self.semantic_model == "grammar_svd":
            data_model = document_embedding.Embedding(
                self.language, self.nlp, "grammar_svd", db_articles)

            vecs = data_model.get_embedding_vectors()
            sim = data_model.get_similarity_matrix()

        return sim, vecs

    def _filter_articles(self, all_articles, db=False):
        after_language = self._check_language(all_articles)
        after_bad_sources = filter_bad_sources(
            self.curate_customer, after_language, db)
        after_bad_articles = filter_bad_articles(
            self.curate_customer, after_bad_sources)

        return after_bad_articles


    def _check_language(self, input_articles):
        language_filtered = []

        for a in input_articles:
            if detect(a.body) == self.language:
                language_filtered.append(a)
            # else:
                # print("Wrong Language")
                # print(a.title)

        print("Good articles")
        print(len(language_filtered))
        return language_filtered


    def _produce_cluster_dict(self, cluster_articles, selected_articles):
        #the point of this method seems to be that returns the subdict of cluster-articles for the selected articles, however, with articlue_curate_instances
        articles_dict = {}
        # produce a dictionary of the clusters
        for center in selected_articles:
            cluster = cluster_articles[center]
        # for center, cluster in article_clusters:
            center_instance = Article_Curate_Query.objects.filter(
                article=center, curate_query=self.query).first()
            all_article_curate_instances = []
            for article in cluster:
                article_curate_instances = Article_Curate_Query.objects.filter(
                    article__title=article.title, curate_query=self.query)
                all_article_curate_instances.extend(article_curate_instances)
            articles_dict[center_instance] = list(
                set(all_article_curate_instances))
            # this output is comprised of article_curate_query instances!
        return articles_dict

    def _produce_and_save_clusters(self, cluster_articles, selected_articles):
        words, samples = self._produce_keywords_and_summaries(
            cluster_articles, selected_articles)
        articles_dict = self._produce_cluster_dict(
            cluster_articles, selected_articles)

        counter = 1

        # in case you go from db:
        old_clusters = Curate_Query_Cluster.objects.filter(
            center__curate_query=self.query)
        old_clusters.delete()

        for key, value in articles_dict.items():
            try:
                keywords = ','.join(words[key.article])
                cluster = Curate_Query_Cluster(rank=counter, center=key, keywords=keywords)
                cluster.save()

                #save the sample into the ar
                key.article.sample = samples[key.article]
                key.article.save()
                
                # cluster.cluster_articles.clear()
                for instance in value:
                    cluster.cluster_articles.add(instance)
                cluster.save()
                counter += 1
            except:
                print('Cannot save cluster')
        self.query.no_clusters = counter
        self.query.save()

    def _produce_keywords_and_summaries(self, cluster_articles, selected_articles):
        # this input dict consists of actual article objects
        representative_model = summarizer.Summarizer(self.language, self.nlp)

        words = representative_model.get_keywords(
            cluster_articles, selected_articles, 2, 30)
        samples = dict([[a, representative_model.create_sample_text(a.body, 300)] for a in selected_articles])
        #alternative_keywords = keywords.keywords_from_articles(cluster_articles, selected_articles, self.language)

        return words, samples

    def _process(self, filtered_articles):

        # filtered_articles = remove_duplicate_articles_for_processing(filtered_articles)

        if filtered_articles:
            sim, vecs = self._semantic_analysis(filtered_articles)

            cluster_articles = clustering_methods.get_clustering(
                filtered_articles, sim, vecs, self.config.getint('general', 'upper_bound'), self.config.getint('general', 'lower_bound'))

            selected_articles = clustering_methods.get_central_articles(
                cluster_articles, self.config.getint('general', 'output_articles'))

            print([a.title for a in selected_articles])
        
        else:
            cluster_articles = []
            selected_articles = []
        
        return cluster_articles, selected_articles

