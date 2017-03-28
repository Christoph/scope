import django
django.setup()

import numpy as np
from textblob import TextBlob

import imaplib
import email
import quopri
import urllib2
from urlparse import urlparse
from datetime import date, timedelta
from tldextract import tldextract

from scipy.cluster.hierarchy import linkage
from scipy.cluster.hierarchy import to_tree
from scipy.spatial.distance import pdist, squareform

from scope.models import Customer
from curate.models import Curate_Query, Article_Curate_Query
from curate.models import Curate_Customer
from scope.models import AgentImap, Agent, Source, Article
from scope.methods.dataprovider import news_handler
from scope.methods.dataprovider import url_extractor, constants
from scope.methods.semantics import embedding
from scope.methods.dataprovider import imap_handler

import scope.methods.semantics.preprocess as preprocess
import scope.methods.semantics.lsi as lsi
import scope.methods.semantics.word_vector as word_vector
from scope.methods.learning import binary_classifier
from scope.methods.graphs import clustering_methods
from scope.methods.graphs import selection_methods
import curate.methods.tests as tests

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF, TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity, rbf_kernel


# initializations
customer_key = "nh"
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
print "GET DATA"

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
    print "============= New Agent ==============="
    if isinstance(con.agent_object, AgentImap):
        print "imap"
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
print len(filtered_articles)

# semantic analysis
print "SEMANTIC ANALYSIS"
lsi_dim = 20

pre = preprocess.PreProcessing(lsi_language_dict[language])
lsi_model = lsi.Model()

vecs = pre.stemm([a.body for a in filtered_articles])
lsi_model.compute(vecs, lsi_dim)

sim = lsi_model.similarity()

# Create embedding model
data_model = embedding.Embedding("en", "grammar_svd", filtered_articles)

vecs_svd = data_model.get_embedding_vectors()
sim_svd = data_model.get_similarity_matrix()

# Compute specific embedding

# clustering
print "CLUSTERING"

# params
params_custom = [[0.001, 0.45, 0.001], [1, 0.01, 1, 15]]

# used params
size_bound = [2, 18]
test = tests.Curate_Test("clusters").test

# custom
selection_custom, threshold = selection_methods.on_average_clustering_test(
    filtered_articles, size_bound, sim, params_custom, test)

center_indices_custom = [i[0] for i in selection_custom['articles']]

selected_articles_custom = [
    filtered_articles[i] for i in center_indices_custom]

# affinity
labels_affinity, center_indices_affinity = clustering_methods.affinity_propagation(sim_svd)

selected_articles_affinity = np.array(filtered_articles)[
    center_indices_affinity]

# gauss
labels_gauss, probas_gauss = clustering_methods.gauss(vecs_svd, 15)

selected_articles_gauss = clustering_methods.get_central_articles(filtered_articles, vecs_svd, labels_gauss)

# hierachical
# Create linkage matrix
linkage_matrix = clustering_methods.hc_create_linkage(vecs_svd)

# Search optimal number of clusters
labels_hc_dist = clustering_methods.hc_cluster_by_distance(linkage_matrix, 0.6)

# Optimize clusters based on the maximum number of clusters allowed
labels_hc_clust = clustering_methods.hc_cluster_by_maxclust(linkage_matrix, 12)

selected_articles_hc, cluster_articles_hc = clustering_methods.get_central_articles(filtered_articles, vecs_svd, labels_hc_clust, True)

# hc tree functions
# tree = to_tree(linkage_matrix)
# tree.pre_order() gives original indicies
# tree.dist gives distance of current index
# tree.count gives leave nodes below current point
