from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from datetime import date

from curate.models import Curate_Customer
from scope.models import Customer

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
            nargs='*',
            default=False,
            help='Send output to specified people',)
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
            curate_customers = Curate_Customer.objects.filter(expires__lt = date.today())
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
                    print selected_articles

                content = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> <html xmlns="http://www.w3.org/1999/xhtml"> <head> <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /> <title>NewsButler brief</title> <meta name="viewport" content="width=device-width, initial-scale=1.0"/> </head> <body style="margin: 0; padding: 0; font-family: Times New Roman, sans-serif;"> <table align="center" border="0" style="border-bottom:0px; border-top:0px; border-color:#aec7e8;" cellpadding="0" cellspacing="0" width="600" style="border-collapse: collapse;"> <!-- Header --> <tr><td align="center" bgcolor="#ffffff" style="padding: 40px 30px 40px 30px;"><h2 style="font-family:Times New Roman, sans-serif;">Hi ' + customer.name + ', your new preselection is ready. Click <a href="' + settings.CURRENT_DOMAIN + '/curate/' + customer.customer_key + '/interface">here</a> to generate the newsletter<hr align="center" width="80%" style="color:#aec7e8;border-color: #aec7e8;border:2px solid;"></tr>'

                recipients = []
                if options['hot']:
                    recipients.append(customer.email) 
                if options['cc'] != False:
                    if len(options['cc']) == 0:
                        recipients.append("admin@scope.ai")
                    else:
                        for i in options['cc']:
                            recipients.append(i)

                if len(recipients) != 0:
                    send_mail('New Scope Pre-Selection available', 'Sorry, this service works only for html-compatible mail clients',
                  'robot@scope.ai', recipients,connection=None,html_message=content)

