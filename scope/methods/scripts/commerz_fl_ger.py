# from django.core.management.base import BaseCommand
import networkx as nx
from random import randint
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
import urllib.request, urllib.error, urllib.parse
import datetime
from datetime import date, timedelta, datetime
from urllib.parse import urlparse
from eventregistry import *
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
from networkx.readwrite import json_graph

# Load custom classses
import semantics.preprocess as preprocess
import dataprovider.news as news
import dataprovider.constants as constants
import semantics.lsi as lsi
import semantics.word_vector as word_vector

# Reload so ipython reloads all submodules each start
reload(preprocess)
reload(news)
reload(constants)
reload(lsi)
reload(word_vector)

reload(sys)

# Set encoding
sys.setdefaultencoding('utf8')

# Instantiate classes
pre = preprocess.PreProcessing("german")
getData = news.Crawler("ger")
lsi_model = lsi.Model()
wv_model = word_vector.Model()


def word_feats(words2):
    return dict([(word2, True) for word2 in words2])

# Fetch the data
data = getData.load_JSON(["Volkswagen", "Volkswagen_Group"])

# Start Proper Semantic Analysis

# Using stemming from the nltk package
# term_vecs = pre.stemm([doc["body"] for doc in data])

# Using spacy and the lemmatizer instead of stemming and nltk
term_vecs, docs = pre.lemma([doc["body"] for doc in data])

lsi_model.compute(term_vecs, 90)

# Train Sentiment Analysis

# negids = movie_reviews.fileids('neg')
# posids = movie_reviews.fileids('pos')

# negfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'neg') for f in negids]
# posfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'pos') for f in posids]

# negcutoff = len(negfeats)*10/11
# poscutoff = len(posfeats)*10/11

# trainfeats = negfeats[:negcutoff] + posfeats[:poscutoff]
# testfeats = negfeats[negcutoff:] + posfeats[poscutoff:]
# #print 'train on %d instances, test on %d instances' % (len(trainfeats), len(testfeats))

# classifier = NaiveBayesClassifier.train(trainfeats)

print("NLP Finished")
# Begin Graph visualisation

# Initialize all graph nodes
ug = nx.Graph()

# Node IDs
counter_add = 0

for a in data:
    # dist_dict = classifier.prob_classify(word_feats(a['body'].split()))
    tup = tuple([int(j) for j in tuple(a['date'].split(
        '-') + a['time'].split(':')) + (0, 1, -1)])
    art_time = datetime.datetime.fromtimestamp(mktime(tup))
    ug.add_node(counter_add, title=a['title'], url=a['url'], suggest=0, summary=a['body'][0:400], images=a['image'], comp=0, source=a['source']['title'], keywords='', time=art_time, sent=randint(0, 100) / 100.)
    # sent =dist_dict.prob("pos"))
    counter_add += 1

graphs = []
score_new = 0
best_thresh = 0.
best_score = 0


# thresh = 0.2
thresh = 0.002

for i in range(0, len(data)):
    # sim = lsi_model.similarity(i)
    sim = wv_model.similarity(docs, i)
    for j in range(i + 1, len(sim)):
        dist = (1. - sim[j]) / 2.
        if dist < thresh:
            ug.add_edge(i, j, {'weight': dist})


# thresh = 0.10

# for s in [x/1000. for x in xrange(0,500)]:

# 	ug.remove_edges_from(ug.edges())

# 	for i in range(0,len( corpus_tfidf )):
# 		sim = index2[ lsi_model2[ corp [ i ] ] ]
# 		for j in range( i+1, len( sim ) ):
# 			dist = (1. - sim[j])/2.
# 			if dist < s and j in ug and i in ug:
# 				ug.add_edge(i,j,{'weight':dist})
# 	graphs = sorted(nx.connected_component_subgraphs(ug),key=len,reverse=True)

# 	test = [x for x in graphs if 30> len(x) >= 5]
# 	exclude = [x.nodes() for x in graphs if x not in test]
# 	test2 = [len(x) for x in test]
# 	if 15 >= len(test) >= 5:
# 		score_new = pow(len(test),2)*sum(test2)

# 	if score_new > best_score:
# 		best_score = score_new
# 		best_thresh = s

# 		print s
# 		print len(graphs)
# 		print score_new
# 		print best_thresh


# dispersion = str((1.-2*best_thresh)*100)[:-2] + '%'
# print best_thresh
# ug.remove_edges_from(ug.edges())
# for i in range( 0, len( corpus_tfidf ) ):
# 	sim = index2[ lsi_model2[ corp [ i ] ] ]
# 	for j in range( i+1, len( sim ) ):
# 		dist = (1. - sim[j])/2.
# 		if dist < best_thresh and j in ug and i in ug:
# 			ug.add_edge(i,j,{'weight':dist})
# graphs = sorted(nx.connected_component_subgraphs(ug),key=len,reverse=True)
# test = [x for x in graphs if 10> len(x) >= 4]
# exclude = [x.nodes() for x in graphs if x not in test]
# for graph in test:
# 	print "\n CLUSTER: \n"
# 	for no in graph:
# 		try:
# 			print ug.node[no]['title'], ug.node[no]['source'], no
# 		except:
# 			pass
# print "\n AND \n"
# for no in list(set().union(*exclude)):
# 	try:
# 		print ug.node[no]['title'], ug.node[no]['source'], no
# 	except:
# 		pass

size = len(data)

tg = nx.DiGraph()
tg.add_node(0, overall_size=size)


gg = nx.DiGraph()
gg.add_node(0, overall_size=size)

count_suggest = 1
count_comp = 1
big_list = []
small_list = []
keywords_in = ['ms', '.', 'cookies', 'cookie', 'mr', '_',
               '-', '2016', 'VW', 'Volkswagen', 'Deutsche Bank', 'DB']

# graphx = sorted([[len(i), nx.average_clustering(i),i] for i in test],reverse=True)

graphs = sorted(nx.connected_component_subgraphs(ug), key=len, reverse=True)
graphx = sorted([[len(i), nx.average_clustering(i), i]
                 for i in graphs], reverse=True)


# ug.remove_nodes_from(list(set().union(*exclude)))


for a in graphx:
    comp = a[2]
    if len(comp) >= 5:

        # first take care of the time signatures of the articles for the detail
        # view
        # collect the different times occuring
        timespartition = sorted(
            list(set([ug.node[i]['time'] for i in comp.nodes()])))
        if len(timespartition) != 0:
            first_time = timespartition[0]
            last_time = timespartition[-1]
            onlytimes = []
            for a in timespartition:
                # partition the set of times into articles with the same
                # timestamp
                onlytimes.append(
                    [i for i in comp.nodes() if ug.node[i]['time'] == a])
            if first_time != last_time:  # in case they're all published at the same time
                time_span = (last_time - first_time).total_seconds()
            else:
                time_span = 1
            # calculate positions on circle, reserving at least 355-5 deg for
            # ones without timestamp.
            notime = [ug.node[i]['time']
                      for i in comp.nodes() if ug.node[i]['time'] is None]
            ratio = len(notime) / len(comp)
            # take care of positioning of articles with the same timestamp

            gg.add_node(count_comp, size=len(comp))
            gg.add_edge(0, count_comp)

            time_bins = time_span / 5.
            for i in range(0, 5):
                lowerbound = first_time + timedelta(seconds=i * time_bins)
                upperbound = first_time + \
                    timedelta(seconds=(i + 1) * time_bins)
                matching_articles = [k for k in comp if (
                    lowerbound <= ug.node[k]['time'] <= upperbound)]
                gg.add_node(count_comp * 100 + i, x=i,
                            y=len(matching_articles), time=lowerbound.isoformat())
                gg.add_edge(count_comp, count_comp * 100 + i)

            for a in onlytimes:
                relcount = 0
                for i in a:
                    if len(a) > 1:
                        ug.node[i]['time_pos'] = (last_time - ug.node[i]['time']).total_seconds() / time_span * 350 * (
                            1 - ratio) + 5 + ratio * 175 + relcount / (len(a) - 1) * 5 - 5 * len(a) / 2
                        relcount += 1
                    else:
                        ug.node[i]['time_pos'] = (last_time - ug.node[i]['time']).total_seconds(
                        ) / time_span * 350 * (1 - ratio) + 5 + ratio * 175
                    # translate into isoformat for display

            # display formatting of time
            if len(notime) == len(comp):  # none of the nodes has a timestamp
                time_disclaim = 'no timestamp for this cluster'
                timeinf = ['', '', '', '', '']
            elif time_span == 1:  # all of those nodes that have a timestamp have the same one
                time_disclaim = 'no timestamp'
                timeinf = ['', '', ug.node[i]['time'].isoformat(), '', '']
            else:
                now = datetime.datetime.now().isoformat()
                now = now[5:7] + '/' + now[8:10] + \
                    ' ' + now[11:13] + 'h <br>(GMT)'
                time_disclaim = 'no timestamp'
                t_hours = time_span / 3600
                if int(t_hours / 4 / 24) == 0:
                    tt1 = str(int(t_hours / 4 % 24)) + 'h'
                elif int(t_hours / 4 % 24) == 0:
                    tt1 = str(int(t_hours / 4 / 24)) + 'd '
                else:
                    tt1 = str(int(t_hours / 4 / 24)) + 'd ' + \
                        str(int(t_hours / 4 % 24)) + 'h'
                if int(t_hours / 2 / 24) == 0:
                    tt2 = str(int(t_hours / 2 % 24)) + 'h'
                elif int(t_hours / 2 % 24) == 0:
                    tt2 = str(int(t_hours / 2 / 24)) + 'd '
                else:
                    tt2 = str(int(t_hours / 2 / 24)) + 'd ' + \
                        str(int(t_hours / 2 % 24)) + 'h'
                if int(3 * t_hours / 4 / 24) == 0:
                    tt3 = str(int(3 * t_hours / 4 % 24)) + 'h'
                elif int(3 * t_hours / 4 % 24) == 0:
                    tt3 = str(int(3 * t_hours / 4 / 24)) + 'd '
                else:
                    tt3 = str(int(3 * t_hours / 4 / 24)) + 'd ' + \
                        str(int(3 * t_hours / 4 % 24)) + 'h'
                if int(t_hours / 24) == 0:
                    tt4 = str(int(t_hours % 24)) + 'h'
                elif int(t_hours / 4 % 24) == 0:
                    tt4 = str(int(t_hours / 4 / 24)) + 'd '
                else:
                    tt4 = str(int(t_hours / 24)) + 'd ' + \
                        str(int(t_hours % 24)) + 'h'
                timeinf = [now, tt1, tt2, tt3, tt4]
        else:
            timeinf = "no time information"
            time_disclaim = "no time information"
        # now for comp level keyword extraction
        # if len(comp) >= 7:
        all_words = []
        for i in comp:
            ug.node[i]['comp'] = count_comp
            ug.node[i]['single'] = 0
            for word in pre.punc.sub('', ug.node[i]['title']).split(" "):
                # print word
                if word not in pre.stop_words and word not in keywords_in:
                    all_words.append(word)
        a = sorted([[len([b for b in all_words if b == word]), word]
                    for word in list(set(all_words))], reverse=True)
        if len(a) >= 2:
            keywords = a[0][1] + ", " + a[1][1]
            keywords_in.append(a[0][1])
            keywords_in.append(a[1][1])
        elif len(a) == 1:
            keywords = a[0][1]
            keywords_in.append(a[0][1])
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
        ordering = sorted(list(closeness.items()),
                          key=lambda close: close[1], reverse=True)
        susvec = ordering[0][0]
        cnode = ug.node[susvec]
        cnode['suggest'] = count_comp
        # q = Suggest(custom= strin, title = ug.node[susvec]['title'], url = ug.node[susvec]['url'], distance = count_comp, images = ug.node[susvec]['images'], keywords = keywords,source=ug.node[susvec]['source'])
        # q.save()

        # add the nodes for the arc
        tg.add_node(count_comp, clustering=clustering, name=keywords)
        tg.add_edge(0, count_comp)

        tg.add_node(count_comp * 100, size=len(comp))
        tg.add_edge(count_comp, count_comp * 100)

        gg.node[count_comp]['name'] = keywords
        # create an array with the number of articles per time bin.

        count_comp += 1
    else:
        ug.remove_nodes_from(comp.nodes())
        ug.remove_edges_from(comp.edges())


# Here the bit for the overall graphic:
# We bin the overall time scale into twenty equally sized bits. Then, for
# each of the bins, we check for the number of articles in every comp that
# appear in this period. Then we create a directed tree graph in which,
# for every cluster, for every slice the number of articles in that period
# is the y-component.


for i in ug.nodes():
    try:
        ug.node[i]['time'] = ug.node[i]['time'].isoformat()
    except:
        ug.node[i]['time'] = ''


tg.add_edge(0, 50)
tg.add_node(5000, size=0.1)
tg.add_edge(50, 5000)
tg.node[0]['final_size'] = len(ug.nodes())
tg.node[0]['comps'] = count_comp - 1
# tg.node[0]['thresh'] = best_thresh
# tg2.node[0]['final_size']=len(ug.nodes())
tg.node[0]['comps'] = count_comp - 1
# tg2.node[0]['thresh'] = best_thresh
ug.graph['size'] = len(ug.nodes())
ug.graph['comps'] = count_comp - 1
# ug.graph['senders'] = senders
# ug.graph['thresh'] = best_thresh
# ug.graph['dispersion'] = dispersion
# ug.graph['tech-nontech-ratio'] = str(tech_ratio)#str(len(doc)/float(articlenumber))#
# ug.graph['wordcount'] = str(words)
# ug.graph['links'] = str(no_urls)
ug.graph['articlenumber'] = str(len(ug))

# export
ug_nl = json_graph.node_link_data(ug)
tgt = json_graph.tree_data(tg, root=0)
ggg = json_graph.tree_data(gg, root=0)
# tgt_mobile = json_graph.tree_data(tg2,root=0)
with open('last24h/static/commerz/tgt_vw2.json', 'w+') as fp:
    # with open('last24h/static/commerz/tgt_vw.json', 'w+') as fp:
    json.dump(tgt, fp)
with open('last24h/static/last24h/tgt_cluster.json', 'w+') as fp:
    json.dump(tgt, fp)

with open('last24h/static/commerz/ggg_vw2.json', 'w+') as fp:
    # with open('last24h/static/commerz/tgt_vw.json', 'w+') as fp:
    json.dump(ggg, fp)
# with open('last24h/static/last24h/cs/cs_'+ strin +'_tgt_mobile.json', 'w+') as fp:
#     json.dump(tgt_mobile,fp)
with open('last24h/static/commerz/ug_vw2.json', 'w+') as fp:
    # with open('last24h/static/commerz/ug_vw.json', 'w+') as fp:
    json.dump(ug_nl, fp)
with open('last24h/static/last24h/ug_nl_cluster.json', 'w+') as fp:
    json.dump(ug_nl, fp)

# send_mail('successful update', 'Successful update. headlines are:' , 'grphtcontact@gmail.com', ['pvboes@gmail.com'])
