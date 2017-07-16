#in this document you just create the selection from the feed articles from within since the last creation
import spacy

from scope.methods.semantics import document_embedding
from scope.methods.graphs import clustering_methods
from scope.methods.semantics import summarizer

# from curate.methods.filters import filter_bad_articles, filter_bad_sources
from reader.models import User_Reader, Reader_Query, Article_Reader_Query, Reader_Query_Cluster

import reader.methods.reader_provider as reader_provider

class Reader(object):
    """Curate process class."""

    def __init__(self, username):
        self.user_reader = User_Reader.objects.get(
            user__username=username)
        self.language = "en"
        self.nlp = spacy.load(self.language)
        self.provider = reader_provider.Reader_Provider(self.nlp)

    def _create_query_instance(self, db=False):
        if db is False:
            self.query = Reader_Query.objects.create(
                user_reader=self.user_reader)
        else:
            self.query = Reader_Query.objects.filter(
                user_reader=self.user_reader).order_by("pk").last()

    def _retrieve_from_sources(self):
        # Get the articles as dict
        db_articles = self.provider.collect_articles(
            self.query)

        print("Number of distinct articles retrieved")
        print(len(db_articles))

        self.query.processed_words = sum([len(i.body) for i in db_articles])
        self.query.articles_before_filtering = len(db_articles)
        self.query.save()

        return db_articles

    def _retrieve_from_db(self):
        article_query_instances = Article_Reader_Query.objects.filter(
            reader_query=self.query)
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
        data_model = document_embedding.Embedding(
                self.language, self.nlp, "grammar_svd", db_articles)

        vecs = data_model.get_embedding_vectors()
        sim = data_model.get_similarity_matrix()

        return sim, vecs

    # def _filter_articles(self, all_articles, db=False):
    #     after_bad_sources = filter_bad_sources(
    #         self.curate_customer, all_articles, db)
    #     after_bad_articles = filter_bad_articles(
    #         self.user_reader, after_bad_sources)

    #     return after_bad_articles

    def _produce_cluster_dict(self, cluster_articles, selected_articles):
        articles_dict = {}
        # produce a dictionary of the clusters
        for center in selected_articles:
            cluster = cluster_articles[center]
        # for center, cluster in article_clusters:
            center_instance = Article_Reader_Query.objects.filter(
                article=center, reader_query=self.query).first()
            all_article_reader_instances = []
            for article in cluster:
                article_reader_instances = Article_Reader_Query.objects.filter(
                    article__title=article.title, reader_query=self.query)
                all_article_reader_instances.extend(article_reader_instances)
            articles_dict[center_instance] = list(
                set(all_article_reader_instances))
            # this output is comprised of article_curate_query instances!
        return articles_dict

    def produce_and_save_clusters(self, cluster_articles, selected_articles):
        words, samples = self.produce_keywords_and_summaries(
            cluster_articles, selected_articles)
        articles_dict = self._produce_cluster_dict(
            cluster_articles, selected_articles)

        counter = 1

        # in case you go from db:
        old_clusters = Reader_Query_Cluster.objects.filter(
            center__reader_query=self.query)
        old_clusters.delete()

        for key, value in articles_dict.items():
            keywords = ','.join(words[key.article])
            cluster = Reader_Query_Cluster(rank=counter, center=key, keywords=keywords)# + ',' + alternative_keywords[key.article])
            cluster.save()

            #save the sample into the article 
            if key.article.sample == None:
                key.article.sample = samples[key.article]
                key.article.save()
            
            # cluster.cluster_articles.clear()
            for instance in articles_dict[key]:
                cluster.cluster_articles.add(instance)
            cluster.save()
            counter += 1
        self.query.no_clusters = counter
        self.query.save()

    def produce_keywords_and_summaries(self, cluster_articles, selected_articles):
        # this input dict consists of actual article objects
        representative_model = summarizer.Summarizer(self.language, self.nlp)

        words = representative_model.get_keywords(
            cluster_articles, selected_articles, 2, 30)
        samples = dict([[a, representative_model.create_sample_text(a.body, 300)] for a in selected_articles])
        #alternative_keywords = keywords.keywords_from_articles(cluster_articles, selected_articles, self.language)

        return words, samples

    def _process(self, filtered_articles):

        # filtered_articles = remove_duplicate_articles_for_processing(filtered_articles)

        #here we need a function to determine the bounds dynamically as a function of the number of input articles and the target number of output articles

        if filtered_articles:
            sim, vecs = self._semantic_analysis(filtered_articles)

            upper_bound = round(pow(len(filtered_articles),0.4))
            lower_bound = round(pow(len(filtered_articles),0.3))
            cluster_articles = clustering_methods.get_clustering(
                filtered_articles, sim, vecs, upper_bound, lower_bound)

            selected_articles = clustering_methods.get_central_articles(
                cluster_articles, self.user_reader.no_output_articles)

            print([a.title for a in selected_articles])

        # you can generate the dict at this point actually.
            self.produce_and_save_clusters(cluster_articles, selected_articles)
        else:
            selected_articles = []
        return selected_articles

    def from_db(self):
        self._create_query_instance(db=True)
        db_articles = self._retrieve_from_db()
        #db_articles = self._filter_articles(db_articles, db=True)
        selected_articles = self._process(db_articles)

        return selected_articles

    def from_sources(self):
        self._create_query_instance(db=False)
        db_articles = self._retrieve_from_sources()
        #db_articles = self._filter_articles(db_articles)
        selected_articles = self._process(db_articles)

        return selected_articles