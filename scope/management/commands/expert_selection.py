from django.core.management.base import BaseCommand
# from django.core.urlresolvers import reverse
# import time
# import urllib
# import threading
# import Queue
# import os
# import datetime
# import sys
# from django.core.mail import send_mail
# from last24h.models import Alert, Send,Sources, Query, Suggest
# #from django_cron import CronJobBase, Schedule                     
# import networkx as nx
# import gensim
# import nltk
# import re
# import string
# import numpy
# import scipy
# import feedparser
# import newspaper
# from newspaper import Article
# import untangle
# #import sys
# import json
# from django.conf import settings
# from django.templatetags.static import static

from last24h.tasks import brief_rene


# global exitFlag, workQueue, queueLock, articlenumber
# from django.conf import settings
# import networkx as nx
# import gensim
# import numpy 
# import scipy
# import nltk
# import re
# import string
# import json
# import urllib
# from networkx.readwrite import json_graph
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')


global workQueue, exitFlag, queueLock,finalurl


class Command(BaseCommand):

    def add_arguments(self, parser):
        #parser.add_argument('thresh', nargs='+', type=str)
        parser.add_argument('string', nargs='+', type=str)
        parser.add_argument('ch1', nargs='+', type=int)
        parser.add_argument('ch2', nargs='+', type=int)
        parser.add_argument('ch3', nargs='+', type=int)
        parser.add_argument('ch4', nargs='+', type=int)
        parser.add_argument('ch5', nargs='+', type=int)
        parser.add_argument('ch6', nargs='+', type=int)


    def handle(self,*args,**options):
        # delivery_t = datetime.datetime.now().replace(second = 0, microsecond = 0, minute = 0) + datetime.timedelta(hours = 1)
        strin = options['string'][0] + "&feeds=none&term=rene_likes_tech"
        args = []
        for i in range(1,7):
            j = options['ch' + str(i)][0]
            #print j
            if j != 0:
                args.append(j)#options['ch' + str(i)][0])

 #        data = json.loads(open(settings.STATIC_ROOT + 'last24h/cs/cs_'+ strin +'_nl.json').read())
 #        strin = strin + "2"
 #        print args, strin
 #        ug = json_graph.node_link_graph(data)
 #        graphs = sorted(nx.connected_component_subgraphs(ug),key=len,reverse=True)
 #        for i in range(1,len(graphs)):
 #            if i not in args:
 #                ug.remove_nodes_from(graphs[i-1].nodes())

 #        ug_nl = json_graph.node_link_data(ug)
 #        with open(settings.STATIC_ROOT + 'last24h/cs/cs_'+ strin +'_nl.json', 'w+') as fp:
 #            json.dump(ug_nl,fp)

 #        address = "Rene"
 #        entry = ['grphtcontact@gmail.com',"Rene's Newsletter", "Rene",strin]
 #        send_mail('Your latest alert for: ' + entry[1], 'Hi' + address + ', here is the link to your latest alert for your query:' + entry[1] +
 # settings.CURRENT_DOMAIN + '/last24h/cs=' + entry[3] + 'You can manage your alerts in your profile settings. Hope you enjoy the graph!', 'grphtcontact@gmail.com', [entry[0]],
 # connection=None, html_message='<head><title>'+ settings.CURRENT_NAME + '| maximise relevance, minimise redundancy</title></head><p>Hi '+
 # address + ',</p><p>here is the link to your latest alert for your query:</p><p><a href="'
 # + settings.CURRENT_DOMAIN + '/last24h/cs=' + entry[3] + '" >' + entry[1] +
 # '</a></p><p>You can manage your alerts in your profile settings. Hope you enjoy the graph!</p>')
        brief_rene('grphtcontact@gmail.com',strin,args)

