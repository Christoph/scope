import research.mi.mutual_information as mi
from curate.convenience.functions import retrieve_objects
from curate.models import Curate_Query

lang = 'en'

customer, curate_customer, queries, articles = retrieve_objects('neuland_herzer', range=1)
q = Curate_Query.objects.filter(curate_customer=curate_customer).first()
article_input = [i.article for i in q.article_curate_query_set.all()][:20]

mut = mi.Mutual_Information(article_input)
mut.ngram_selection(3,1,1,lang)

