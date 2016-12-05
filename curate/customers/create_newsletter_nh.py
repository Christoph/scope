from operator import mul
from networkx.readwrite import json_graph
import networkx as nx
import gensim
import re
import nltk
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
# from django.core.mail import send_mail
from time import mktime
from datetime import datetime
# from last24h.models import Suggest
# from django.conf import 'last24h/static/rt numpy
import scipy
import email
import imaplib
import os
import sys
import urllib2
import datetime
from datetime import date, timedelta, datetime
from urlparse import urlparse
from eventregistry import *
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
from networkx.readwrite import json_graph

from scope.models import Article, Customer
from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer

import scope.methods.semantics.preprocess as preprocess
import scope.methods.semantics.word_vector as word_vector
import scope.methods.cluster.graphBuilder as builder
import scope.methods.dataprovider.crawler as Crawler

import scope.methods.graphs.graphBuilder as builder
import scope.methods.graphs.tests.rev_engineer as test
import scope.methods.graphs.selector as selector


def byteify(input):
    # Turns unicode into UTF-8
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


sys.setdefaultencoding('utf8')

pre = preprocess.PreProcessing("english")
wv_model = word_vector.Model()
crawler = Crawler.Crawler("imap")

db_articles = []

customer = Customer.objects.get(name="Neuland Herzer")
curate_customer = Curate_Customer.objects.get(customer=customer)
curate_query = Curate_Query.objects.create(curate_customer=curate_customer)

# Load data
data = crawler.query_source("NH")

for a in data:
    art, created = Article.objects.get_or_create(
        title=a['titles'], url=a['urls'], defaults={
            'body': a['body'], 'images': a['images'],
            'description': a['description']})

    Article_Curate_Query.objects.create(article=art, curate_query=curate_query)
    db_articles.append(art)

# Begin Semantic Analysis

doc = [d["body"] for d in data]

term_vecs, docs = pre.lemma([d for d in doc])

sim = wv_model.similarity(docs)

# Begin Graph visualisation

ug = nx.Graph()

for i in range(0, len(data)):
    try:
        source = urlparse(urls[i]).hostname
    except:
        source = "No Source Information"

    ug.add_node(i, title=data[i]["title"], url=data[i]["url"], suggest=0, summary=data[i]["description"][0:200],
                images=data[i]["images"], comp=0, source=source, keywords='',
                time=None)

ug_nl = json_graph.node_link_data(ug)

graphs = []
score_new = 0
best_thresh = 0.
best_score = 0

# Optimization
for s in [x / 10000. for x in xrange(1, 201)]:

    # while score_new >= score_old:#len(graphs) not in [5,6] and any(len(x) <4
    # for x in graphs):

    # Remove old edges
    ug.remove_edges_from(ug.edges())

    for i in range(0, len(data)):
        # TODO: SIMILARITY
        sim = wv_model.similarity(docs, i)
        for j in range(i + 1, len(sim)):
            dist = (1. - sim[j])
            if dist < s and j in ug and i in ug:
                ug.add_edge(i, j, {'weight': dist})
    graphs = sorted(nx.connected_component_subgraphs(ug),
                    key=len, reverse=True)

    test = [x for x in graphs if 20 > len(x) >= 3]
    exclude = [x.nodes() for x in graphs if x not in test]
    # test2 = [len(x) for x in test]
    if len(test) >= 2:
        # len(test[0])+len(test[1])#sum(test2)#len(test)#test2[0]
        score_new = len(test)
        # score_new = [len(test),sum(test2)]

    # score_new = sum(test2) #[len(test),sum(test2)]

    if score_new > best_score and len(test) >= 3:
        best_score = score_new
        best_thresh = s

        # print thresh
        # thresh += 0.001
        print s
        print len(graphs)
        # for i in graphs:
        #     for ii in i:
        #         print ug.node[ii]['title']
        #     print "and"
        # print test2
        print score_new
        print best_thresh
        # if thresh >= 0.5:
        #     break


dispersion = str((1. - 2 * best_thresh) * 100)[:-2] + '%'
print best_thresh
ug.remove_edges_from(ug.edges())
for i in range(0, len(data)):
    sim = wv_model.similarity(docs, i)
    # sim = index2[lsi_model2[corp[i]]]
    for j in range(i + 1, len(sim)):
        dist = (1. - sim[j])
        if dist < best_thresh and j in ug and i in ug:
            ug.add_edge(i, j, {'weight': dist})
graphs = sorted(nx.connected_component_subgraphs(ug), key=len, reverse=True)
test = [x for x in graphs if 20 > len(x) >= 3]
exclude = [x.nodes() for x in graphs if x not in test]

for graph in test:
    print "\n CLUSTER: \n"
    for no in graph:
        try:
            print ug.node[no]['title'], ug.node[no]['source'], no
        except:
            pass
print "\n AND \n"
for no in list(set().union(*exclude)):
    try:
        print ug.node[no]['title'], ug.node[no]['source'], no
    except:
        pass
size = len(data)

# Tg is inner circle
tg = nx.DiGraph()
tg.add_node(0, overall_size=size)

count_suggest = 1
count_comp = 1
big_list = []
small_list = []
keywords_in = ['ms', '.', 'cookies', 'cookie', 'mr', '_', '-', '2016']


graphx = sorted([[len(i), nx.average_clustering(i), i]
                 for i in test], reverse=True)  # 0:min(5,len(graphs)-1)]
# for i in range(min(6,len(graphs))):
#     ug.remove_nodes_from(graphs[i])

print "\n REPRESENTATIVE: \n"

for a in graphx:
    comp = a[2]

    # Redundant
    if len(comp) >= 3:
            # now for comp level keyword extraction
            # if len(comp) >= 7:
        all_words = []
        for i in comp:
            ug.node[i]['comp'] = count_comp
            ug.node[i]['single'] = 0
            for word in preprocess.punc.sub(
                    '', ug.node[i]['title']).split(" "):
                # print word
                if word not in preprocess.stop_words:
                    all_words.append(word)
        a = sorted([[len([b for b in all_words if b == word]), word]
                    for word in list(set(all_words))], reverse=True)
        if len(a) >= 2:
            keywords = a[0][1] + ", " + a[1][1]
        elif len(a) == 1:
            keywords = a[0][1]
            # keywords_in.append(keywords[0])
            # keywords_in.append(keywords[1])
        else:
            keywords = ''

        # clustering for detail view
        if nx.average_clustering(comp) == 1:
            clustering = 100
        else:
            clustering = str(nx.average_clustering(comp))[2:4]

        # compute the centrality to turn them into one detail view and the
        # radius size
        count_degree = 1
    # elif len(comp) in [4,5]:
        closeness = nx.closeness_centrality(comp, distance=True)
        # for [b,a] in sorted([[closeness[r],r] for r in comp.nodes()],
        # reverse=True):
        for (a, b) in sorted([[a, nx.degree(comp)[a]] for a in nx.degree(comp)], key=lambda close: close[1], reverse=True):
            ug.node[a]['deg'] = b
            ug.node[a]['deg_pos'] = float(count_degree) / len(comp) * 360
            count_degree += 1
        ordering = sorted(closeness.items(),
                          key=lambda close: close[1], reverse=True)
        # Most central article ID
        susvec = ordering[0][0]
        cnode = ug.node[susvec]
        cnode['suggest'] = count_comp

        print cnode["title"] + "\n"

        # q = Suggest(custom=strin, title=ug.node[susvec]['title'], url=ug.node[susvec][
                    # 'url'], distance=count_comp, images=ug.node[susvec]['images'], keywords=keywords, source=ug.node[susvec]['source'])
        # q.save()
        # q = Suggest(title=ug.node[susvec]['title'], url=ug.node[susvec]['url'], rank=count_comp, images=ug.node[
                    # susvec]['images'], keywords=keywords, source=ug.node[susvec]['source'])
        # q.save()

        # add the nodes for the arc
        tg.add_node(count_comp, clustering=clustering, name=keywords)
        tg.add_edge(0, count_comp)

        tg.add_node(count_comp * 100, size=len(comp))
        tg.add_edge(count_comp, count_comp * 100)
        count_comp += 1
    else:

        ug.remove_nodes_from(comp)


# tg.add_edge(0,50)
# tg.add_node(5000, size= 0.1)
# tg.add_edge(50,5000)
# tg.node[0]['final_size']=len(ug.nodes())
# tg.node[0]['comps'] = count_comp-1
# #tg.node[0]['thresh'] = best_thresh
# #tg2.node[0]['final_size']=len(ug.nodes())
# tg.node[0]['comps'] = count_comp-1
# #tg2.node[0]['thresh'] = best_thresh
# ug.graph['size']=len(ug.nodes())
# ug.graph['comps'] = count_comp-1
# ug.graph['senders'] = senders
# ug.graph['thresh'] = best_thresh
# ug.graph['dispersion'] = dispersion
# #ug.graph['tech-nontech-ratio'] = str(tech_ratio)#str(len(doc)/float(articlenumber))#
# ug.graph['wordcount'] = str(words)
# ug.graph['links'] = str(no_urls)
# ug.graph['articlenumber'] = str(articlenumber)

# export
# ug_nl = json_graph.node_link_data(ug)
# tgt = json_graph.tree_data(tg,root=0)
# #tgt_mobile = json_graph.tree_data(tg2,root=0)
# with open('nh/static/nh/json/' + date.today().isoformat() + '_center.json', 'w+') as fp:
#     json.dump(tgt,fp)

# with open('nh/static/nh/json/' + date.today().isoformat() + '_graph.json', 'w+') as fp:
#     json.dump(ug,fp)


# q = Query.objects.filter(string= strin)
# for query in q:
#     query.articlenumber = articlenumber
#     query.words = words
#     query.save()

#send_mail('successful update', 'Successful update. headlines are:' , 'grphtcontact@gmail.com', ['pvboes@gmail.com'])
