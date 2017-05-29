global exitFlag, workQueue, queueLock, articlenumber
from django.conf import settings
import networkx as nx
import gensim
import numpy
import scipy
import nltk
import re
import string
import json
import urllib.request, urllib.parse, urllib.error
from networkx.readwrite import json_graph
import sys
reload(sys)
sys.setdefaultencoding('utf8')
#checks = open("rene_checks.txt", 'w+')
# #     json.dump(ug_nl,fp)

dict = gensim.corpora.Dictionary.load(settings.STATIC_ROOT + 'rene/rene_data/rene.dict')
corp = gensim.corpora.MmCorpus(settings.STATIC_ROOT + 'rene/rene_data/rene.mm')
lsi_model = gensim.models.LsiModel.load(settings.STATIC_ROOT + 'rene/rene_data/rene.lsi')
index = gensim.similarities.MatrixSimilarity.load(settings.STATIC_ROOT + 'rene/rene_data/rene.index')
#corpus_tfidf = gensim.corpora.MmCorpus('/tmp/corpus_tf.mm')
data = json.loads(open(settings.STATIC_ROOT + 'rene/rene_all.json').read())
ug = json_graph.node_link_graph(data)
#import json graph and assign from another graph
size= len(corp)

tfidf_model = gensim.models.TfidfModel( corp )
corpus_tfidf= tfidf_model[corp]

# gensim.corpora.MmCorpus.serialize(settings.STATIC_ROOT + 'rene/rene_data/rene.mm',corp)#/home/django/graphite/static/last24h/l24h.mm', corp)
# dict.save(settings.STATIC_ROOT + 'rene/rene_data/rene.dict')
# lsi_model.save(settings.STATIC_ROOT + 'rene/rene_data/rene.lsi')
# index.save(settings.STATIC_ROOT + 'rene/rene_data/rene.index')
#lda_model.save('/tmp/model.lda')

#n1=5

#corpus_tfidf= tfidf_model[corp]

lsi_model2 = gensim.models.LsiModel(corpus_tfidf, id2word=dict, num_topics=n1) #
corpus_lsi = lsi_model2[corpus_tfidf]
# list_corpus = []
# for dox in corpus_lsi:
#     list_corpus.append(dox)
index2 = gensim.similarities.SparseMatrixSimilarity(corpus_lsi, num_features = n1 )

lsi_model2.save(settings.STATIC_ROOT + 'rene/rene_data/l24h2.lsi')
index2.save(settings.STATIC_ROOT + 'rene/rene_data/l24h2.index')
#Begin Graph visualisation

#3-articlenumber*0.03/500#0.1/pow(upper/210,2)  #the higher the thresh, the more critical

graphs = []
score_new = 0
score_old = [0,0]#-1
best_thresh = 0.
best_score = 0#[0,0]
graphs_old = []
#thresh = 0.02

#Now trying two steps: In the first, get the bigguest cluster (which should correspond to tech topics) and then in a second step maximise the number of clusters in it

# orignumber = len(ug)
# print "First Round"
# print str(len(ug)) + " old graph"

for s in [x*0.0025 for x in range(0,200)]:


#while score_new >= score_old:#len(graphs) not in [5,6] and any(len(x) <4 for x in graphs):
    ug.remove_edges_from(ug.edges())

    for i in range( 0, len( corpus_tfidf ) ):
        sim = index2[ lsi_model2[ corp [ i ] ] ]
        for j in range( i+1, len( sim ) ):
            dist = (1. - sim[j])/2.
            if dist < s:
                ug.add_edge(i,j,{'weight':dist})
    graphs = sorted(nx.connected_component_subgraphs(ug),key=len,reverse=True)
    test = [x for x in graphs if len(x) >= 3]#20>=
    exclude = [x.nodes() for x in graphs if x not in test]
    test2 = [len(x) for x in test]
    if len(test) >= 2:
        score_new = len(test[0])+len(test[1])#sum(test2)#len(test)#test2[0]
        #score_new = [len(test),sum(test2)]


    #graphs_old = graphs
    if score_new > best_score and len(test) >= 3:
        best_score = score_new
        best_thresh = s
        #print best_thresh


print(best_thresh)
ug.remove_edges_from(ug.edges())
for i in range( 0, len( corpus_tfidf ) ):
    sim = index2[ lsi_model2[ corp [ i ] ] ]
    for j in range( i+1, len( sim ) ):
        dist = (1. - sim[j])/2.
        if dist < best_thresh and j in ug and i in ug:
            ug.add_edge(i,j,{'weight':dist})

graphs = sorted(nx.connected_component_subgraphs(ug),key=len,reverse=True)
test = [x for x in graphs if len(x) >= 3]
for graph in test:
    print("\n CLUSTER: \n")
    for no in graph:
        try:
            print(ug.node[no]['title'], ug.node[no]['source'], no)
        except:
            pass
print("\n AND \n")
for no in list(set().union(*exclude)):
    try:
        print(ug.node[no]['title'], ug.node[no]['source'], no)
    except:
        pass

print("\n SECOND ROUND \n")


for i in range(1,len(graphs)):
    ug.remove_nodes_from(graphs[i].nodes())
    #print "deleted" + str(graphs[i].nodes())



#n2 = 15
#corpus_tfidf= tfidf_model[corp]

lsi_model = gensim.models.LsiModel(corpus_tfidf, id2word=dict, num_topics=n2) #
corpus_lsi = lsi_model[corpus_tfidf]
# list_corpus = []
# for dox in corpus_lsi:
#     list_corpus.append(dox)
index = gensim.similarities.SparseMatrixSimilarity(corpus_lsi, num_features = n2 )

lsi_model.save(settings.STATIC_ROOT + 'rene/rene_data/l24h3.lsi')
index.save(settings.STATIC_ROOT + 'rene/rene_data/l24h3.index')
#Begin Graph visualisation

#3-articlenumber*0.03/500#0.1/pow(upper/210,2)  #the higher the thresh, the more critical

score_new = 0
best_thresh = 0.
best_score = 0#[0,0]
#thresh = 0.02



for s in [x*0.001 for x in range(0,500)]:


#while score_new >= score_old:#len(graphs) not in [5,6] and any(len(x) <4 for x in graphs):
    ug.remove_edges_from(ug.edges())

    for i in range( 0, len( corpus_tfidf ) ):
        sim = index[ lsi_model[ corp [ i ] ] ]
        for j in range( i+1, len( sim ) ):
            dist = (1. - sim[j])/2.
            if dist < s and j in ug and i in ug:
                ug.add_edge(i,j,{'weight':dist})
    graphs = sorted(nx.connected_component_subgraphs(ug),key=len,reverse=True)
    test = [x for x in graphs if 20 >= len(x) >= 3]#20>=
    exclude = [x.nodes() for x in graphs if x not in test]
    test2 = [len(x) for x in test]
    if len(test) != 2:
        score_new = len(test)#len(test[0])+len(test[1])#sum(test2)#len(test)#test2[0]
        #score_new = [len(test),sum(test2)]


    #graphs_old = graphs
    if score_new > best_score and len(test) >= 3:
        best_score = score_new
        best_thresh = s
        # print best_score, s
        # for graph in test:
        #     print "\n CLUSTER: \n"
        #     for no in graph:
        #         try:
        #             print ug.node[no]['title'], ug.node[no]['source'], no
        #         except:
        #             pass
        # print "\n AND \n"
        # for no in list(set().union(*exclude)):
        #     try:
        #         print ug.node[no]['title']
        #     except:
        #         pass

print(best_thresh)
ug.remove_edges_from(ug.edges())
for i in range( 0, len( corpus_tfidf ) ):
    sim = index[ lsi_model[ corp [ i ] ] ]
    for j in range( i+1, len( sim ) ):
        dist = (1. - sim[j])/2.
        if dist < best_thresh and j in ug and i in ug:
            ug.add_edge(i,j,{'weight':dist})

graphs = sorted(nx.connected_component_subgraphs(ug),key=len,reverse=True)
test = [x for x in graphs if 20 >= len(x) >= 3]
for graph in test:
    print("\n CLUSTER: \n")
    for no in graph:
        try:
            print(ug.node[no]['title'], ug.node[no]['source'], no)
        except:
            pass
print("\n AND \n")
for no in list(set().union(*exclude)):
    try:
        print(ug.node[no]['title'], ug.node[no]['source'], no)
    except:
        pass
