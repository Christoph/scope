import django
django.setup()

import numpy as np
import json
from django.core import serializers

from scope.models import Article

import scope.methods.semantics.word_vector as word_vector
from test.clustering import cluster_plot as plt
import scope.methods.semantics.lsi as lsi
import scope.methods.semantics.preprocess as preprocess

wv = word_vector.Model("en")
pre = preprocess.PreProcessing("english")
lsi_model = lsi.Model()

# Helper functions
def normalize_vecs(vecs):
    min_v = np.min(vecs)
    max_v = np.max(vecs)

    out = (vecs-min_v)/(max_v - min_v)

    return out

# GET DATA FROM JSON
with open('test/clustering/articles.json', 'r') as stream:
    data = json.load(stream)

articles = []
for obj in serializers.deserialize("json", data):
    articles.append(obj.object)

# GET SEMANTIC INFORMATION
wv.load_data(articles)
vecs = wv.document_vectors()
nvecs = normalize_vecs(vecs)
sim_wv = wv.similarity_matrix()

word_vecs = pre.stemm([a.body for a in articles])
lsi_model.compute(word_vecs, 20)
sim_lsi = lsi_model.similarity()


# Compare Clusterings
# labels = labels = get_labels(sim, nvecs)
# plt.plot_compare_clustering(nvecs, labels.values(), labels.keys())
