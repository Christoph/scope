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
        parser.add_argument('upper_bond', nargs='+', type=int)
        parser.add_argument('weight1', nargs='+', type=float)
		parser.add_argument('weight2', nargs='+', type=float)

    def handle(self,*args,**options): 
    	sys.argv = ['curate/customers/curate_newsletter_process.py', customer_key, lower_step, upper_step, step_size, lower_bound, upper_bound, weight1, weight2]
        execfile('curate/customers/curate_newsletter_process.py')
        send_mail('successful update', 'go to <a href="127.0.0.1:8000/curate/nh/interface> here</a>' , 'robot@scope.ai', ['pvboes@gmail.com'])
