from celery import shared_task
from tracking.models import Curate_Click_Event, Curate_Open_Event, Source_Click_Event
from curate.models import Article_Curate_Query, Curate_Recipient, Curate_Query
from scope.models import Source
from django.utils import timezone


@shared_task
def process_click_event(tracking_result):
	#the mails contain query and recipoient pk as well as the tracked articles url (or news source url)
	tracked_url = tracking_result.tracked_url
	query_pk = tracking_result.metadata['query_pk']
	recipient_pk = tracking_result.metadata['recipient_pk']
	try:
		instance = Article_Curate_Query.objects.get(curate_query__pk=query_pk, article__url=tracked_url)
		recipient = Curate_Recipient.objects.get(pk=recipient_pk)
		event = Curate_Click_Event(article_curate_query=instance, recipient=recipient, time_opened=timezone.now())
		event.save()

	except:
		try:
			source = Source.objects.get(url=tracked_url)
			recipient = Curate_Recipient.objects.get(pk=recipient_pk)
			event = Source_Click_Event(source=source, recipient=recipient, time_opened=timezone.now())
			event.save()

		except:
			print("Problem processing tracked_url:" + tracked_url)

@shared_task
def process_open_event(tracking_result):
	#the mails contain query and recipoient pk as well as the tracked articles url (or news source url)
	tracked_url = tracking_result.tracked_url
	query_pk = tracking_result.metadata['query_pk']
	recipient_pk = tracking_result.metadata['recipient_pk']
	try:
		query = Curate_Query.objects.get(pk=query_pk)
		recipient = Curate_Recipient.objects.get(pk=recipient_pk)
		event = Curate_Open_Event(curate_query=query, recipient=recipient, time_opened=timezone.now())
		event.save()
		
	except:
		print("Problem processing tracked_url:" + tracked_url)
