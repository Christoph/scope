import django
django.setup()

import numpy as np

from scope.models import Customer
from curate.models import Curate_Query, Article_Curate_Query
from curate.models import Curate_Customer

import scope.methods.semantics.word_vector as word_vector
from scope.methods.learning import binary_classifier

# params
customer_key = "neuland_herzer"
min_count = 100
language = "eng"


# initializations
wv_language_dict = {
    'ger': 'de',
    'eng': 'en',
}
wv_model = word_vector.Model(wv_language_dict[language])
classifier = binary_classifier.binary_classifier(
    wv_model.pipeline, customer_key)

# get data from db
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

db_articles = []
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

filtered_articles = classifier.classify_by_count(
    db_articles, min_count)

print "articles after classification"
print len(filtered_articles)
for article in filtered_articles:
    print article.title

# semantic analysis
print "SEMANTIC ANALYSIS"


# clustering
print "CLUSTERING"


# select articles
print "SELECT ARTILCES"
