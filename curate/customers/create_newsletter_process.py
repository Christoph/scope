import sys

# from curate.models import Select

import scope.methods.semantics.preprocess as preprocess
import scope.methods.semantics.word_vector as word_vector
import scope.methods.graphs.selector as selector
import scope.methods.dataprovider.provider as provider

from scope.models import Article, Customer, Agent
from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer

reload(sys)
sys.setdefaultencoding('utf8')

pre = preprocess.PreProcessing("english")
wv_model = word_vector.Model("en")
data_provider = provider.Provider()

db_articles = []
words = 0

customer = Customer.objects.get(name="Neuland Herzer Test")
curate_customer = Curate_Customer.objects.get(customer=customer)
curate_query = Curate_Query.objects.create(curate_customer=curate_customer)

# Load data

# Get all sources connected to the curate_customer
source = Agent.objects.get(
    product_customer_id=curate_customer.id)

agent = source.agent_object

# Get the articles as dict
data = data_provider.query_source(agent)

# Save the articles into the database
for a in data:

    source = Source.objects.get_or_create(url = a['url'].netloc)
    art, created = Article.objects.get_or_create(
        title=a['title'],
        url=a['url'],
        defaults={"source": source, "body": a['body'], "images": a['images'], "description": a['description']})

    Article_Curate_Query.objects.get_or_create(
        article=art, curate_query=curate_query)
    db_articles.append(art)

# Semantic Analysis
wv_model.load_data(db_articles)

sim = wv_model.similarity_matrix()

# Extract Selection


def test(dict, test_params):
    cluster_lengths = [i[0] for i in dict['articles']]
    weight_cluster_size = test_params[0]
    weight_coverage = test_params[1]
    return weight_cluster_size * dict['no_clusters'] + weight_coverage * sum(cluster_lengths) / dict['no_articles']


test_params = [1, 1]
# [range, step], test_params
params = [[0, 0.5, 0.001], test_params]

sel = selector.Selection(len(db_articles), sim)


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
