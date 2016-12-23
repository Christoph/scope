import sys

# from curate.models import Select

import scope.methods.semantics.preprocess as preprocess
import scope.methods.semantics.word_vector as word_vector
import scope.methods.graphs.selector as selector
import scope.methods.dataprovider.provider as provider

from scope.models import Customer
from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer

from curate.scripts import curate_process

reload(sys)
sys.setdefaultencoding('utf8')

# customer_key = "neuland_herzer"
# model = "lsi"
# lower_step = 0
# upper_step = 0.5
# step_size = 0.01
# lower_bound = 6
# upper_bound = 20
# weight1 = 1
# weight2 = 0
# lsi_dim = 20


def test(stats, weights):
    cluster_lengths = [i[0] for i in stats['articles']]
    weight_cluster_size = weights[0]
    weight_coverage = weights[1]
    return weight_cluster_size * stats['no_clusters'] + weight_coverage * sum(cluster_lengths) / stats['no_articles']


test_params = [weight1, weight2]
params = [[lower_step, upper_step, step_size], test_params]
size_bound = [lower_bound, upper_bound]

curate = curate_process.Curate(
    model=model,
    customer_key=customer_key,
    test=test,
    params=params,
    size_bound=size_bound,
    lsi_dim=lsi_dim)

selected_articles = curate.from_sources()
print selected_articles
