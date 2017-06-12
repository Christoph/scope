from django.core.management.base import BaseCommand
from datetime import date

from curate.models import Curate_Customer
from scope.models import Customer
from curate.methods.mail import send_notification

from curate.methods import curate_process

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('customer_key', nargs='+', type=str)
        parser.add_argument(
            '--hot', 
            dest='hot',
            action='store_true',
            default=False,
            help='Send output to customer',)
        parser.add_argument(
            '--cc', 
            dest='cc',
            action='store_true',
            #nargs='*',
            default=False,
            help='Send output to admin',)
        parser.add_argument(
            '--print', 
            action="store_true",
            dest='print',
            default=False,
            help='Print selected articles to console',)
        parser.add_argument(
            '--db', 
            action="store_true",
            dest='db',
            default=False,
            help='Create from database',)

    def handle(self, *args, **options):
        if  options['customer_key'][0] == 'all':
            curate_customers = Curate_Customer.objects.filter(expires__gt = date.today())
            customers = [i.customer for i in curate_customers]
        else:
            customers = [Customer.objects.get(customer_key=options['customer_key'][0])]
        for customer in customers:
                customer_key = customer.customer_key
                curate = curate_process.Curate(customer_key=customer_key)
                if options['db']:
                    selected_articles = curate.from_db()
                else:
                    selected_articles = curate.from_sources()

                if options['print']:
                    print(selected_articles)

                send_notification(customer_key, options['hot'], options['cc'])
    
                    


