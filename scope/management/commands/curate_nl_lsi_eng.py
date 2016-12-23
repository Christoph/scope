from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import sys

from scope.models import Customer




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
        parser.add_argument('lsi_dim', nargs='+', type=int)

    def handle(self, *args, **options):
        customer_key = options['customer_key'][0]
        lower_step = options['lower_step'][0]
        upper_step = options['upper_step'][0]
        step_size = options['step_size'][0]
        lower_bound = options['lower_bound'][0]
        upper_bound = options['upper_bound'][0]
        weight1 = options['weight1'][0]
        weight2 = options['weight2'][0]
        lsi_dim = options['lsi_dim'][0]
        sys.argv = ['curate/customers/create_newsletter_process.py', customer_key,
                    lower_step, upper_step, step_size, lower_bound, upper_bound, weight1, weight2, lsi_dim]
        execfile('curate/customers/create_nl_lsi.py')
        customer = Customer.objects.get(customer_key=customer_key)
        content = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> <html xmlns="http://www.w3.org/1999/xhtml"> <head> <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /> <title>NewsButler brief</title> <meta name="viewport" content="width=device-width, initial-scale=1.0"/> </head> <body style="margin: 0; padding: 0; font-family: Times New Roman, sans-serif;"> <table align="center" border="0" style="border-bottom:0px; border-top:0px; border-color:#aec7e8;" cellpadding="0" cellspacing="0" width="600" style="border-collapse: collapse;"> <!-- Header --> <tr><td align="center" bgcolor="#ffffff" style="padding: 40px 30px 40px 30px;"><h2 style="font-family:Times New Roman, sans-serif;">Hi ' + customer.name + ', your new preselection is ready. Click <a href="' + settings.CURRENT_DOMAIN + '/curate/' + customer.customer_key + '/interface">here</a> to generate the newsletter<hr align="center" width="80%" style="color:#aec7e8;border-color: #aec7e8;border:2px solid;"></tr>'
        send_mail('New Scope Pre-Selection available', 'Sorry, this service works only for html-compatible mail clients',
                  'robot@scope.ai', [customer.email, 'paul@scope.ai','christoph@scope.ai'],connection=None,html_message=content)
