from __future__ import absolute_import

from celery import shared_task

from django.core.mail import send_mail
from curate.methods.mail import send_newsletter

@shared_task
def send_newsletter_task(customer_key):
	send_newsletter(customer_key)

	def on_failure(self, *args, **kwargs):
	 	send_mail(subject = "Failure with newsletter sending for customer: " + customer_key, message="", from_email="robot@scope.ai", recipient_list =['admin@scope.ai'])   

@shared_task
def selection_made_task(customer_key):
	send_mail(subject = customer_key + " made selection." + customer_key, message="", from_email="robot@scope.ai", recipient_list =['admin@scope.ai'])   