from django.core.management.base import BaseCommand
import networkx as nx
import gensim
import nltk
import re
import string
import feedparser
import newspaper
from newspaper import Article
import Queue
import threading
import time
import untangle
import sys
import json
import urllib
import math
from django.core.mail import send_mail
from time import mktime
from datetime import datetime
from last24h.models import Suggest
from django.templatetags.static import static
from django.conf import settings


class Command(BaseCommand):

    def handle(self,*args,**options): 

<<<<<<< HEAD
#        send_mail('successful update', 'Successful update. headlines are:' , 'grphtcontact@gmail.com', ['pvboes@gmail.com'])

=======
        import numpy
        import scipy
        execfile(settings.STATIC_BREV + static('last24h/create_homegraph.py'))
        send_mail('successful update', 'Successful update. headlines are:' , 'grphtcontact@gmail.com', ['pvboes@gmail.com'])
>>>>>>> 0e6be549595571122208beecd20114063c47bd07
