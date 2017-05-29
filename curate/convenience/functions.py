from curate.models import Curate_Customer, Curate_Query, Article_Curate_Query
from scope.models import Customer, Agent, AgentImap
import configparser
import csv
from django.utils.encoding import smart_str
from datetime import date


def create_customer_from_config_file(customer_key):
	# Create imap agent
	config = configparser.RawConfigParser()

	config.read('curate/customers/' + customer_key + "/" + customer_key + '.cfg')
	user = config.get('imap', 'user')
	pwd = config.get('imap', 'pwd')
	imap = config.get('imap', 'imap')
	mailbox = config.get('imap', 'mailbox')
	interval = config.get('imap', 'interval')
	language = config.get('general', 'language')

	agentimap, created = AgentImap.objects.get_or_create(user=user, pwd=pwd, imap=imap, mailbox=mailbox, interval=interval)
	if created:
		agentimap.save()

	# Create Customer
	customer, created = Customer.objects.get_or_create(name=customer_key,  customer_key=customer_key)
	if created:
		customer.save()

	# Create Curate Customer
	curate_customer, created = Curate_Customer.objects.get_or_create(customer=customer, expires=date.today())
	if created:
		curate_customer.save()

	# Create curate_query
	query, created = Curate_Query.objects.get_or_create(curate_customer=curate_customer)
	if created:
		query.save()

	return customer, curate_customer, query, agentimap, language


def retrieve_objects(customer_key, range=None):
    customer = Customer.objects.get(customer_key=customer_key)
    curate_customer = Curate_Customer.objects.get(customer=customer)
    if range != None:
        # queries = Curate_Query.objects.filter(time_stamp__gt=date.today()-timedelta(days=range))
        queries = Curate_Query.objects.filter(
            curate_customer=curate_customer).order_by("pk").reverse()[0:range]
        articles = Article_Curate_Query.objects.filter(
            curate_query__in=queries).all()
        return customer, curate_customer, queries, articles
    return customer, curate_customer


def export_csv(queryset):
    file = open('queryset2string.csv', 'w+')
    writer = csv.writer(file, csv.excel)
    # produce titles
    writer.writerow([
        smart_str("ID"),
        smart_str("Title"),
        smart_str("Description"),
    ])
    # write datat
    for obj in queryset:
        writer.writerow([
            smart_str(obj.pk),
            smart_str(obj.title),
            smart_str(obj.description),
        ])
