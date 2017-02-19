import django
django.setup()

import numpy as np

from scope.models import Customer
from curate.models import Curate_Query, Article_Curate_Query
from curate.models import Curate_Customer

import scope.methods.semantics.preprocess as preprocess
import scope.methods.semantics.lsi as lsi
import scope.methods.semantics.word_vector as word_vector
from scope.methods.learning import binary_classifier
from scope.methods.graphs import clustering_methods
from scope.methods.graphs import selection_methods
import curate.methods.tests as tests

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF, TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity, rbf_kernel, sigmoid_kernel

# initializations
customer_key = "neuland_herzer"
language = "eng"

db_articles = []
threshold = 0.0
wv_language_dict = {
    'ger': 'de',
    'eng': 'en',
}
lsi_language_dict = {
    'ger': 'german',
    'eng': 'english',
}
wv_model = word_vector.Model(wv_language_dict[language])
classifier = binary_classifier.binary_classifier(
    wv_model.pipeline, customer_key)

# GET DATA
print "GET DATA"

customer = Customer.objects.get(
    customer_key=customer_key)
curate_customer = Curate_Customer.objects.get(
    customer=customer)
query = Curate_Query.objects.filter(
    curate_customer=curate_customer).order_by("pk").reverse()[0]
article_query_instances = Article_Curate_Query.objects.filter(
    curate_query=query)
for i in article_query_instances:
    i.rank = 0
    i.save()

all_articles = [i.article for i in article_query_instances]

bad_sources = curate_customer.bad_source.all()

# check if duplicate titles exist and remove them
titles = [a.title for a in all_articles]
u, indices = np.unique(titles, return_index=True)
all_articles = np.array(all_articles)[indices]
all_articles = all_articles.tolist()

for a in all_articles:
    if a.source not in bad_sources:
        db_articles.append(a)

print "articles:"
print len(db_articles)

words = sum([len(i.body) for i in db_articles])

# CLASSIFY
print "CLASSIFY"
min_count = 100
classifier_type = "none"  # none, nn300

if classifier_type == "nn300":
    filtered_articles = classifier.classify_by_count(
        db_articles, min_count)
else:
    print "no classifier selected"
    filtered_articles = db_articles

print "articles after classification"
print len(filtered_articles)

# semantic analysis
print "SEMANTIC ANALYSIS"
lsi_dim = 20

pre = preprocess.PreProcessing(lsi_language_dict[language])
lsi_model = lsi.Model()

vecs = pre.stemm([a.body for a in filtered_articles])
lsi_model.compute(vecs, lsi_dim)

sim = lsi_model.similarity()

# test three different dim reduction methods
vectorizer = TfidfVectorizer(
    sublinear_tf=True, min_df=1, stop_words='english', max_df=0.9)
tfidf = vectorizer.fit_transform([a.body for a in filtered_articles])

# similarities
sim_tfidf_cos = cosine_similarity(tfidf)
sim_tfidf_rbf = rbf_kernel(tfidf)
sim_tfidf_sig = sigmoid_kernel(tfidf)

nmf = NMF(n_components=100, random_state=1,
          alpha=.1, l1_ratio=.5).fit_transform(tfidf)

sim_nmf_cos = cosine_similarity(nmf)
sim_nmf_rbf = rbf_kernel(nmf)
sim_nmf_sig = sigmoid_kernel(nmf)

# is like lsi
svd = TruncatedSVD(n_components=100, random_state=1).fit_transform(tfidf)

sim_svd_cos = cosine_similarity(svd)
sim_svd_rbf = rbf_kernel(svd)
sim_svd_sig = sigmoid_kernel(svd)

# clustering
print "CLUSTERING"
print "test ER as validation field"

used_sim = sim_nmf_cos

# custom
size_bound = [2, 18]
params_lsi = [[0.001, 0.5, 0.001], [1, 0.01, 1, 15]]
test = tests.Curate_Test("clusters").test

selection_custom, threshold = selection_methods.on_average_clustering_test(
    filtered_articles, size_bound, used_sim, params_lsi, test)

labels_custom = clustering_methods.sim_based_threshold(used_sim, threshold)

selected_articles_custom = [
    filtered_articles[i[0]] for i in selection_custom['articles']]

# affinity
labels_affinity, center_indices_affinity = clustering_methods.affinity_propagation(used_sim)

selected_articles_affinity = np.array(filtered_articles)[
    center_indices_affinity]

# kmeans
# labels_kmeans, center_indices_kmeans = clustering_methods.k_means(
#     tfidf, 12)

# selected_articles_kmeans = tfidf[center_indices_kmeans]

# select articles analysis
print "artilces count"
print len(selected_articles_custom)

print "selected_articles"
for a in selected_articles_custom:
    print a
