import networkx as nx
import gensim
import nltk
import re
import string
import json
import urllib
from networkx.readwrite import json_graph

from last24h.models import Suggest
        
def db_suggestions(graph,maxcount,filt= None):
    
    sug = sorted([[d['suggest'],n] for n,d in graph.nodes_iter(data=True)])
    for i in range (0, maxcount):
        q = Suggest(id = i, title = graph.node[sug[i][1]]['title'], url = graph.node[sug[i][1]]['url'], custom = 'None',summary = graph.node[sug[i][1]]['summary'] )
        q.save()

#load from gensim objects

dict = gensim.corpora.Dictionary.load('last24h/static/last24h/l24h.dict')
corp = gensim.corpora.MmCorpus('last24h/static/last24h/l24h.mm')
lsi_model = gensim.models.LsiModel.load('last24h/static/last24h/l24h.lsi')
index = gensim.similarities.MatrixSimilarity.load('last24h/static/last24h/l24h.index')
#corpus_tfidf = gensim.corpora.MmCorpus('/tmp/corpus_tf.mm')
data = json.loads(open('last24h/static/last24h/ug_nl.json').read())
ug = json_graph.node_link_graph(data)
#import json graph and assign from another graph
size= len(corp)

ug.remove_edges_from(ug.edges())
for i in ug.nodes():
    ug.node[i]['suggest'] = 0
    
#Begin Graph visualisation

thresh = 0.15#0.1/pow(size/400.,2)  #the higher the thresh, the more critical  

for i in range( 0, len( corp ) ):
  
    sim = index[ lsi_model[ corp [ i ] ] ]
    for j in range( i+1, len( sim ) ):
        dist = (1. - sim[j])/2.
        if dist < thresh:
            ug.add_edge(i,j,{'weight':dist})

#cliques = list(nx.find_cliques(ug))
#closeness = nx.closeness_centrality(ug, distance=True)

count_suggest = 1
graphs = sorted(nx.connected_component_subgraphs(ug), key = len, reverse = True)
for comp in graphs:
    closeness = nx.closeness_centrality(comp, distance=True)
    if len(comp) > 5:
        for i in sorted(list(nx.find_cliques(comp)),key = len, reverse=True):
            if len(i) > 3:
                susvec = sorted([[closeness[r],r] for r in i], reverse=True)[0][1]
                if (False not in [ug.node[n]['suggest'] == 0 for n in ug.neighbors(susvec)]) and (ug.node[susvec]['suggest'] == 0):
                    ug.node[susvec]['suggest'] = 'count_suggest'
                    count_suggest += 1
    elif len(comp) in [2,3,4,5]:
        susvec = sorted(closeness.items(), key = lambda close:close[1],reverse=True)[0][0]
        ug.node[susvec]['suggest'] = 'count_suggest'
        count_suggest += 1
            
    else: 
        ug.node[comp.nodes()[0]]['suggest'] = 'count_suggest'
        count_suggest += 1

#give_suggestions(ug,15)

db_suggestions(ug,15)

from networkx.readwrite import json_graph

ug_nl = json_graph.node_link_data(ug)  
#ug_tree = json_graph.tree_data(ug) #hier soll noch rein, dass der Graph nach Keywords und query sortiert wird: In der Mitte die Query, dann die Keywords und dann die Artikel
ug_adj = json_graph.adjacency_data(ug)

with open('last24h/static/last24h/ug_nl.json', 'w') as fp:
    json.dump(ug_nl,fp)
    
#with open('ug_tree.json', 'w') as fp:
 #   json.dumps(json_ug, fp)
    
with open('last24h/static/last24h/ug_adj.json', 'w') as fp:
    json.dump(ug_adj, fp)