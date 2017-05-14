from curate.models import Curate_Customer, Curate_Query, Article_Curate_Query
from scope.models import Customer
import csv
from django.utils.encoding import smart_str
#from datetime import date, timedelta

def retrieve_objects(customer_key, range=None):
	customer = Customer.objects.get(customer_key=customer_key)
	curate_customer = Curate_Customer.objects.get(customer=customer)
	if range != None:
		#queries = Curate_Query.objects.filter(time_stamp__gt=date.today()-timedelta(days=range))
		queries = Curate_Query.objects.filter(curate_customer=curate_customer).order_by("pk").reverse()[0:range]
		articles = Article_Curate_Query.objects.filter(curate_query__in=queries).all()
		return customer, curate_customer, queries, articles
	return customer, curate_customer


def export_csv(queryset):
	file = open('queryset2string.csv', 'w+')
	writer = csv.writer(file, csv.excel)
	#produce titles
	writer.writerow([
		smart_str(u"ID"),
		smart_str(u"Title"),
		smart_str(u"Description"),
	])
	#write datat
	for obj in queryset:
		writer.writerow([
			smart_str(obj.pk),
			smart_str(obj.title),
			smart_str(obj.description),
		])
