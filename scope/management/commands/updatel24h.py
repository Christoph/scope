from django.core.management.base import BaseCommand
import networkx as nx
import gensim
import nltk
import re
import string
import feedparser
import newspaper
from newspaper import Article
import queue
import threading
import time
import untangle
import sys
import json
import urllib.request, urllib.parse, urllib.error
import math
from django.core.mail import send_mail
from time import mktime
from datetime import datetime
from django.conf import settings


class Command(BaseCommand):

    def handle(self,*args,**options): 
        import numpy
        import scipy
        exec(compile(open('explore/scripts/create_homegraph.py').read(), 'explore/scripts/create_homegraph.py', 'exec'))
       # send_mail('successful update', 'Successful update. headlines are:' , 'grphtcontact@gmail.com', ['pvboes@gmail.com'])
