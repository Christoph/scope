from __future__ import absolute_import

from celery import shared_task, current_task
from django.conf import settings
from django.templatetags.static import static

@shared_task
def test_task(email):
	print email 

@shared_task
def brief_rene(email,strin,select):
	#import networkx as nx
	#import gensim
	#import nltk
	#import re
	#import string
	#import json
	#import urllib
	#from networkx.readwrite import json_graph
	#from django.core.mail import send_mail
	#from last24h.models import Suggest
	#from django.conf import settings
#	try:
	#sys.argv = [email]
	sys.argv = [settings.STATIC_BREV + static('last24h/create_brief_rene.py'), strin, email,select]
	execfile(settings.STATIC_ROOT + 'last24h/create_brief_rene.py')


@shared_task
def sample_brief(email):
	#import networkx as nx
	#import gensim
	#import nltk
	#import re
	#import string
	#import json
	#import urllib
	#from networkx.readwrite import json_graph
	#from django.core.mail import send_mail
	#from last24h.models import Suggest
	#from django.conf import settings
	#try:
	#sys.argv = [email]
	execfile(settings.STATIC_ROOT + 'last24h/create_brief.py')
	#except:
	#	raise Exception()

@shared_task
def cs_task(feeds,strin,alert):
	#from celery import shared_task, current_task
	#import gensim
	#import nltk
	#import re
	#import string
	import numpy
	import scipy
	#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
	sys.argv = [settings.STATIC_BREV + static('last24h/customsearch.py'), feeds, strin, current_task,alert]
				#return returncode
	if alert == 0:
		current_task.update_state(state='PREPARE',
			meta={'current': 10, 'articles':0, 'words':0})
	
	execfile(settings.STATIC_ROOT + 'last24h/customsearch.py')#settings.STATIC_BREV + static('last24h/cs2.py'))
	#except:
	#	raise Exception()
			
	def on_failure(self, *args, **kwargs):
	 	pass
