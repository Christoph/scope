import django
django.setup()


from scope.models import Customer
from curate.models import Curate_Query, Article_Curate_Query
from curate.models import Curate_Customer

# params
customer_key = "neuland_herzer"


# get data from db
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

print "initial articles:"
print len(all_articles)

# check articles
db_articles = []
bad_sources = curate_customer.bad_source.all()

for a in all_articles:
    if a.source not in bad_sources:
        db_articles.append(a)

print "good articles:"
print len(db_articles)

words = sum([len(i.body) for i in db_articles])

# classify


# semantic analysis


# clustering


# select articles
