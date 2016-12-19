import sys
from datetime import date

# from curate.models import Select

import scope.methods.semantics.preprocess as preprocess
import scope.methods.semantics.lsi as lsi
import scope.methods.graphs.selector as selector

from scope.models import Customer
from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer

reload(sys)
sys.setdefaultencoding('utf8')

pre = preprocess.PreProcessing("english")
lsi_model = lsi.Model()

# will be replaced by authentication
customer = Customer.objects.get(name=customer_key)
curate_customer = Curate_Customer.objects.get(customer=customer)
last_query = Curate_Query.objects.filter(
        curate_customer=curate_customer).filter(time_stamp=date.today())[0]
article_query_instances = Article_Curate_Query.objects.filter(
        curate_query=last_query)
db_articles = [i.article for i in article_query_instances]


words = sum([len(i.body) for i in db_articles])

# Semantic Analysis
vecs = pre.stemm([a.body for a in db_articles])
lsi_model.compute(vecs, lsi_dim)

sim = lsi_model.similarity()

# Extract Selection


def test(dictionary, test_params):
    cluster_lengths = [i[0] for i in dictionary['articles']]
    weight_cluster_size = test_params[0]
    weight_coverage = test_params[1]
    return weight_cluster_size * dictionary['no_clusters'] + weight_coverage * sum(cluster_lengths) / dictionary['no_articles']


test_params = [weight1, weight2]
# [range, step], test_params
params = [[lower_step, upper_step, step_size], test_params]

sel = selector.Selection(len(db_articles), sim)

selection = sel.by_test(test, params, [upper_bound, lower_bound])
selected_articles = [db_articles[i[0]] for i in selection['articles']]

# Database object creation
last_query.processed_words = words
last_query.no_clusters = selection[
                    'no_clusters']
last_query.clustering = selection['clustering']
last_query.save()

for i in range(0, len(selected_articles)):
    a = Article_Curate_Query.objects.get(article=selected_articles[i])
    a.rank = i + 1
    a.save()
