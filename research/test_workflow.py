import django
django.setup()

import spacy

from scope.models import Agent

from scope.methods.semantics import document_embedding
from scope.methods.semantics import summarizer
from scope.methods.dataprovider import provider

from scope.methods.graphs import clustering_methods
from curate.convenience import functions as helper

from importlib import reload


# initializations
customer_key = "test_customer"

max_clusters = 24
min_clusters = 6
n_centers = 5
summary_max_len = 100


# GET DATA
print("GET DATA")

customer, curate_customer, query, agentimap, language = helper.create_customer_from_config_file(customer_key)

# agent = Agent(
#     product_customer_object=curate_customer,
#     agent_object=agentimap
# )
# agent.save()

print("Loading Spacy")
nlp = spacy.load(language)
print("Spacy Loaded")

# From mail
fetcher = provider.Provider(nlp)

# Get all sources connected to the curate_customer
db_articles = fetcher.collect_from_agents(
    curate_customer, query, language)

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

words = representative_model.get_keywords(cluster_articles)
# rep = representative_model.text_rank(cluster_articles, max_size=summary_max_len)

print("RESULTS")
out = []
for i in range(0, len(cluster_articles)):
    out.append({
        "central_title": cluster_articles[i][0].title,
        "keywords": words[i]
        # "representative": rep[i]
        })
