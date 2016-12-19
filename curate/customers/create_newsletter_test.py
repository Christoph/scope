import sys
import numpy as np

# from curate.models import Select

import scope.methods.semantics.preprocess as preprocess
import scope.methods.semantics.word_vector as word_vector
import scope.methods.graphs.selector as selector
import scope.methods.dataprovider.provider as provider
import scope.methods.semantics.lsi as lsi


from scope.models import Customer
from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer

from scope.models import AgentImap, Agent, Source, Article, AgentEventRegistry

from scope.methods.dataprovider import imap_handler, er_handler

reload(sys)
sys.setdefaultencoding('utf8')

pre = preprocess.PreProcessing("english")
lsi_model = lsi.Model()
wv_model = word_vector.Model("en")
data_provider = provider.Provider()

customer_key = "nh"
lower_step = 0.5
upper_step = 1
step_size = 0.01
lower_bound = 2
upper_bound = 16
weight1 = 1
weight2 = 0

customer = Customer.objects.get(customer_key=customer_key)
curate_customer = Curate_Customer.objects.get(customer=customer)
curate_query = Curate_Query.objects.create(curate_customer=curate_customer)

# Load data

# Collect and save articles to the database
db_articles = data_provider.collect_from_agents(curate_customer, curate_query)

words = sum([len(i.body) for i in db_articles])

# Semantic Analysis
wv_model.load_data(db_articles)
sim = wv_model.similarity_matrix()

vecs = pre.stemm([a.body for a in db_articles])
lsi_model.compute(vecs, 100)

sim_lsi = lsi_model.similarity()

# Extract Selection


def test(dict, test_params):
    cluster_lengths = [i[0] for i in dict['articles']]
    weight_cluster_size = test_params[0]
    weight_coverage = test_params[1]
    return weight_cluster_size * dict['no_clusters'] + weight_coverage * sum(cluster_lengths) / dict['no_articles']

def test_labels(labels, params):
    selected = len(labels) - np.sum(labels == np.max(labels))
    if selected == 0:
        coverage = 1
    else:
        coverage = selected/len(labels)
    max_clust = np.max(np.bincount(labels.astype(int)))
    return params["coverage_weight"] * coverage + params["max_clust_weight"] * max_clust

test_params = [weight1, weight2]
# [range, step], test_params
params = [[lower_step, upper_step, step_size], test_params]

sel = selector.Selection(len(db_articles), sim_lsi)


selection = sel.by_test(test, params, [2, 15])
selected_articles = [db_articles[i[0]] for i in selection['articles']]

# Database object creation
curate_query.processed_words = words
curate_query.no_clusters = selection[
    'no_clusters']
curate_query.clustering = selection['clustering']
curate_query.save()

for i in range(0, len(selected_articles)):
    a = Article_Curate_Query.objects.get(
        article=selected_articles[i], curate_query=curate_query)
    a.rank = i + 1
    a.save()
