from django.core.management.base import BaseCommand
from django.core.mail import send_mail

import sys


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('customer_key', nargs='+', type=str)
        parser.add_argument('lower_step', nargs='+', type=float)
        parser.add_argument('upper_step', nargs='+', type=float)
        parser.add_argument('step_size', nargs='+', type=float)
        parser.add_argument('lower_bound', nargs='+', type=int)
        parser.add_argument('upper_bound', nargs='+', type=int)
        parser.add_argument('weight1', nargs='+', type=float)
        parser.add_argument('weight2', nargs='+', type=float)

    def handle(self, *args, **options):
        customer_key = options['customer_key'][0]
        lower_step = options['lower_step'][0]
        upper_step = options['upper_step'][0]
        step_size = options['step_size'][0]
        lower_bound = options['lower_bound'][0]
        upper_bound = options['upper_bound'][0]
        weight1 = options['weight1'][0]
        weight2 = options['weight2'][0]
        sys.argv = ['curate/customers/create_newsletter_process.py', customer_key,
                    lower_step, upper_step, step_size, lower_bound, upper_bound, weight1, weight2]
        execfile('curate/customers/create_nl_lsi.py')
        send_mail('successful update', 'go to <a href="127.0.0.1:8000/curate/nh/interface> here</a>',
                  'robot@scope.ai', ['pvboes@gmail.com'],'go to <a href="127.0.0.1:8000/curate/nh/interface> here</a>')
