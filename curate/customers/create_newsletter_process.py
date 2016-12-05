import sys

# from curate.models import Select

import scope.methods.semantics.preprocess as preprocess
import scope.methods.semantics.word_vector as word_vector
import scope.methods.graphs.selector as selector
import scope.methods.dataprovider.provider as provider

from scope.models import Article, Customer, Source
from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer

reload(sys)
sys.setdefaultencoding('utf8')

pre = preprocess.PreProcessing("english")
wv_model = word_vector.Model()
data_provider = provider.Provider()

db_articles = []
words = 0

customer = Customer.objects.get(name="Neuland Herzer")
curate_customer = Curate_Customer.objects.get(customer=customer)
curate_query = Curate_Query.objects.create(curate_customer=curate_customer)

# Load data

# Get all sources connected to the curate_customer
source = Source.objects.get(
    product_customer_id=curate_customer.id)

agent = source.agent_object

# Get the articles as dict
data = provider.query_source(agent)

# Save the articles into the database
for a in data:
    art, created = Article.objects.get_or_create(
        source=source,
        title=a['title'],
        url=a['url'],
        body=a['body'],
        images=a['images'],
        description=a['description'])

    Article_Curate_Query.objects.create(article=art, curate_query=curate_query)
    db_articles.append(art)

words = sum([len(i.body) for i in db_articles])

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

selection = sel.by_test(test, params, [3, 20])
selected_articles = [db_articles[i[0]] for i in selection['articles']]

# Database object creation
curate_query.update(processed_words=words, no_clusters=selection[
                    'no_clusters'], clustering=selection['clustering'])
curate_query.save()

for i in range(0, len(selected_articles)):
    a = Article_Curate_Query.objects.get(article=selected_articles[i])
    a.rank = i + 1
    a.save()
