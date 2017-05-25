import django
django.setup()

import numpy as np
from textblob import TextBlob

from tldextract import tldextract

from curate.models import Curate_Query
from curate.models import Curate_Customer
from scope.models import Customer
from scope.models import AgentImap, Agent, Source, Article
from scope.methods.semantics import document_embedding
from scope.methods.semantics import summarizer
from scope.methods.dataprovider import imap_handler

import scope.methods.semantics.preprocess as preprocess
import scope.methods.semantics.lsi as lsi
from scope.methods.graphs import clustering_methods


# initializations
customer_key = "neuland_herzer"
language = "eng"

threshold = 0.0
wv_language_dict = {
    'ger': 'de',
    'eng': 'en',
}
lsi_language_dict = {
    'ger': 'german',
    'eng': 'english',
}

# GET DATA
print("GET DATA")

customer = Customer.objects.get(
    customer_key=customer_key)
curate_customer = Curate_Customer.objects.get(
    customer=customer)
query = query = Curate_Query.objects.create(
    curate_customer=curate_customer)

# From mail
db_articles = []
mails = []

# Get all sources connected to the curate_customer
connector = Agent.objects.filter(
    product_customer_id=curate_customer.id)

for con in connector:
    print("============= New Agent ===============")
    if isinstance(con.agent_object, AgentImap):
        print("imap")
        imap = imap_handler.ImapHandler(con.agent_object, language)

        mails = imap.get_data_new()

for a in mails:
    source, created = Source.objects.get_or_create(
        url=a['source'],
        defaults={"name": tldextract.extract(a['source']).domain.title()})

    art, created = Article.objects.get_or_create(
        title=a['title'],
        url=a['url'],
        defaults={"source": source, "body": a['body'],
                  "images": a['images'], "pubdate": a['pubdate']})

    db_articles.append(art)

filtered_articles = db_articles
print(len(filtered_articles))

# semantic analysis
print("SEMANTIC ANALYSIS")
lsi_dim = 20

pre = preprocess.PreProcessing(lsi_language_dict[language])
lsi_model = lsi.Model()

vecs = pre.stemm([a.body for a in filtered_articles])
lsi_model.compute(vecs, lsi_dim)

sim = lsi_model.similarity()

# Create embedding model
data_model = document_embedding.Embedding("en", "grammar_svd", filtered_articles)

vecs_svd = data_model.get_embedding_vectors()
sim_svd = data_model.get_similarity_matrix()

# clustering
print("CLUSTERING")

selected_articles, cluster_articles = clustering_methods.get_clustering(filtered_articles, sim_svd, vecs_svd, 16)

print("KEYWORDS & SUMMARY/REPRESENTATIVE")

representative_model = summarizer.Summarizer("en")

words = representative_model.get_keywords(cluster_articles)
rep = representative_model.text_rank(cluster_articles, max_size=100)

print("RESULTS")
out = []
for i in range(0, len(cluster_articles)):
    out.append({
        "central_title": cluster_articles[i][0].title,
        "keywords": words[i],
        "representative": rep[i]
        })
