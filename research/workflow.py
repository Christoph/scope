import django
django.setup()

import spacy

from scope.models import Agent

from scope.methods.semantics import document_embedding
from scope.methods.semantics import summarizer
from scope.methods.dataprovider import provider

from scope.models import Customer
from curate.models import Article_Curate_Query, Curate_Query, Curate_Customer
from scope.methods.graphs import clustering_methods
from curate.convenience import functions as helper

from importlib import reload


# initializations
customer_key = "test_customer"

max_clusters = 30
min_clusters = 10
n_centers = 15
summary_max_len = 100
language = "de"


# GET DATA
print("GET DATA")

print("Loading Spacy")
nlp = spacy.load(language)
print("Spacy Loaded")

# From mail

# customer, curate_customer, query, agentimap, language = helper.create_customer_from_config_file(customer_key)

# agent = Agent(
#     product_customer_object=curate_customer,
#     agent_object=agentimap
# )
# agent.save()

# fetcher = provider.Provider(nlp)
#
# # Get all sources connected to the curate_customer
# db_articles = fetcher.collect_from_agents(
#     curate_customer, query, language)
#
# filtered_articles = db_articles
#
# print((len(filtered_articles)))

# From db
customer = Customer.objects.get(
    customer_key=customer_key)
curate_customer = Curate_Customer.objects.get(
    customer=customer)

query = Curate_Query.objects.filter(
    curate_customer=curate_customer).order_by("pk").last()

article_query_instances = Article_Curate_Query.objects.filter(
    curate_query=query)
for i in article_query_instances:
    i.rank = 0
    i.save()
db_articles = [i.article for i in article_query_instances]

filtered_articles = db_articles

print((len(filtered_articles)))

# semantic analysis
print("SEMANTIC ANALYSIS")

# Create embedding model
data_model = document_embedding.Embedding(language, nlp, "grammar_svd", filtered_articles)

vecs = data_model.get_embedding_vectors()
sim = data_model.get_similarity_matrix()

# clustering
print("CLUSTERING")

cluster_articles = clustering_methods.get_clustering(filtered_articles, sim, vecs, max_clusters, min_clusters)

central_articles = clustering_methods.get_central_articles(cluster_articles, n_centers)

print("KEYWORDS & SUMMARY/REPRESENTATIVE")

representative_model = summarizer.Summarizer(language, nlp)

summaries = representative_model.text_rank(cluster_articles, central_articles, 300)

words = representative_model.get_keywords(cluster_articles, central_articles, 1, 30)

samples = dict([[a, representative_model.create_sample_text(a.body, 300)] for a in central_articles])

print("RESULTS")
out = []
for i in range(0, len(cluster_articles)):
    out.append({
        "central_title": list(cluster_articles.keys())[i].title,
        "keywords": words[list(cluster_articles.keys())[i]]
        })
