import sys
import json

# from curate.models import Select

import scope.methods.semantics.preprocess as preprocess
import scope.methods.semantics.word_vector as word_vector
import scope.methods.graphs.selector as selector

from scope.models import Article, Customer
from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer

reload(sys)
sys.setdefaultencoding('utf8')

customer = Customer.objects.get(name="Neuland Herzer")
curate_customer = Curate_Customer.objects.get(customer=customer)
curate_query = Curate_Query.objects.create(curate_customer=curate_customer)

with open('curate/data/data.json') as fp:
    data = json.load(fp)

db_articles = []

for a in data:
    art, created = Article.objects.get_or_create(title=a['titles'], url=a['urls'], defaults={
                                                 'body': a['body'], 'images': a['images'], 'description': a['description']})
    Article_Curate_Query.objects.create(article=art, curate_query=curate_query)
    db_articles.append(art)

counter = 0
words = 0

doc = [i['body'] for i in data]

words = sum([len(i) for i in doc])

# Begin Semantic Analysis
pre = preprocess.PreProcessing("english")
wv_model = word_vector.Model()

term_vecs, docs = pre.lemma([d for d in doc])
sim = wv_model.similarity(docs)


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
