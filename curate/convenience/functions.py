from curate.models import Curate_Customer, Curate_Query, Article_Curate_Query, Curate_Customer_Selection, Curate_Rejection_Reasons, Curate_Recipient
from scope.models import Customer, AgentImap, Agent
from django.contrib.contenttypes.models import ContentType
import configparser
import csv
from django.utils.encoding import smart_str
from datetime import date


def create_customer_from_config_file(customer_key, selection_options=False):
    # Create imap agent
    config = configparser.RawConfigParser()

    config.read('curate/customers/' + customer_key +
                "/" + customer_key + '.cfg')
    user = config.get('imap', 'user')
    pwd = config.get('imap', 'pwd')
    imap = config.get('imap', 'imap')
    mailbox = config.get('imap', 'mailbox')
    interval = config.get('imap', 'interval')
    language = config.get('general', 'language')


    agentimap, created = AgentImap.objects.get_or_create(
        user=user, pwd=pwd, imap=imap, mailbox=mailbox, interval=interval)

    # Create Customer
    name = config.get('meta', 'name')
    email = config.get('meta', 'email')
    customer, created = Customer.objects.get_or_create(
        name=name, customer_key=customer_key, email=email)

    # Create Curate Customer
    curate_customer, created_customer = Curate_Customer.objects.get_or_create(
        customer=customer, defaults={'expires': date.today()})

    # create agent
    cur_cus_contenttype = ContentType.objects.get(model="curate_customer")
    agent_imap_contenttype = ContentType.objects.get(model="agentimap")
    agent, created = Agent.objects.get_or_create(
        product_customer_type=cur_cus_contenttype, product_customer_id=curate_customer.id, agent_type=agent_imap_contenttype, agent_id=agentimap.id)

    # Create curate_query
    query = Curate_Query(
        curate_customer=curate_customer)

    query.save()

    if selection_options:
        #Create Curate Selections and Rejection Reasons 
        options = dict(
            [['choose', {'kind': 'sel', 'color': '#30c96d'}],
             ['avoid', {'kind': 'mis', 'color': '#f95738',
                        'reasons': [{'name': 'bad source', 'kind': 'sou'},
                                    {'name': 'bad content', 'kind': 'con'},
                                    {'name': 'too frequent', 'kind': 'frq'}
                                    ]
                        }
              ]
             ]
        )

        for key, value in options.items():
            selection, created = Curate_Customer_Selection.objects.get_or_create(
                curate_customer=curate_customer, name=key, defaults={'kind': value['kind'], 'color': value['color']})
            if 'reasons' in value:
                for reason in value['reasons']:
                    Curate_Rejection_Reasons.objects.get_or_create(
                        selection=selection, name=reason['name'], kind=reason['kind'])

    # Create Source for the Curate_Customer
    # agent = Agent(
    #     product_customer_object=curate_customer,
    #     agent_object=agentimap
    # )

    return customer, curate_customer, query, agentimap, language

def update_mail_recipients(customer_key):
    config = configparser.RawConfigParser()

    config.read('curate/customers/' + customer_key +
                "/" + customer_key + '.cfg')

    customer, curate_customer = retrieve_objects(customer_key)
    #Delete old recipients
    Curate_Recipient.objects.filter(curate_customer=curate_customer).delete()

    #Create new Recipients
    recipients = config.get('outlet', 'recipients').split(';\n')
    for i in recipients:
        l = i.split(',')
        if len(l)==3:
            l = [w.replace(';','').strip() for w in l]
            rec = Curate_Recipient(curate_customer=curate_customer, email=l[0], first=l[1], last=l[2])
            rec.save()
            print('created recipient', rec)
        else:
            print('problem with parsing recipient', l)


def retrieve_objects(customer_key, range=None):
    customer = Customer.objects.get(customer_key=customer_key)
    curate_customer = Curate_Customer.objects.get(customer=customer)
    if range != None:
        # queries =
        # Curate_Query.objects.filter(time_stamp__gt=date.today()-timedelta(days=range))
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
