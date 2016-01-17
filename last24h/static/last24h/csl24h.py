import networkx as nx
import gensim
import nltk
import re
import string

import json
from networkx.readwrite import json_graph
from last24h.models import Suggest
    

    
        
#load from gensim objects

data = json.loads(open('last24h/static/last24h/ug_nl.json').read())
ug = json_graph.node_link_graph(data)
lsi_model = gensim.models.LsiModel.load('last24h/static/last24h/l24h.lsi')
dicte = gensim.corpora.Dictionary.load('last24h/static/last24h/l24h.dict')
index = gensim.similarities.MatrixSimilarity.load('last24h/static/last24h/l24h.index')


for i in ug.nodes():
    ug.node[i]['suggest'] = 0

sims = []
for topic in topics:
    vec_bow = dicte.doc2bow(topic.split('_'))
    vec_lsi = lsi_model[vec_bow]
    sim = index[vec_lsi]
    w = sorted(enumerate(sim), key = lambda list: -list[1])
    sims = sims +  w



q = Suggest.objects.filter(custom = 'q'+ strin)
q.delete()


max_count = 15
thresh = 0.3 #the higher the thresh, the more critical
count_suggest = 1

for i in sorted(sims, key = lambda list: -list[1]):#[0:len(sims)-1]:
    if ug.node[i[0]]['suggest'] == 0:
        if count_suggest < max_count:
            ug.node[i[0]]['suggest'] = count_suggest
            q = Suggest(custom= 'q'+ strin, title = ug.node[i[0]]['title'], url = ug.node[i[0]]['url'], distance = count_suggest, images = ug.node[i[0]]['images'])
            q.save()
            count_suggest += 1
        else: 
            break 
#    diste = (1. - i[1])/2.
#    if diste < thresh:
           
            
graphs = sorted(nx.connected_component_subgraphs(ug), key = len, reverse = True)
for graph in graphs:
    if len([n for n in graph.nodes_iter(data=True) if n[1]['suggest'] != 0]) == 0:
        ug.remove_nodes_from(graph)


#use this function later on to produce reading suggestions               
#graphs = sorted(nx.connected_component_subgraphs(ug), key = len, reverse = True)
#count_suggest = 1
#for comp in graphs:
#    if len(comp) > 1:
#        closeness = nx.closeness_centrality(comp, distance=True)
#        susvec = sorted(closeness.items(), key = lambda close:close[1],reverse=True)[0][0]
#        ug.node[susvec]['suggest'] = count_suggest
#        count_suggest += 1
#    else:
#        ug.node[comp.nodes()[0]]['suggest'] = count_suggest
#        count_suggest += 1

#give_suggestions(ug,15)


#draw = 0
#if draw == 1:
 #   graph_draw(ug,pos=pos,vertex_color = set,vertex_text_position=-0.5, vertex_text_color=(0., 0., 0., 1.),output="vs.png")
    
ug_cs_nl = json_graph.node_link_data(ug)  
#ug_tree = json_graph.tree_data(ug) #hier soll noch rein, dass der Graph nach Keywords und query sortiert wird: In der Mitte die Query, dann die Keywords und dann die Artikel
#ug_cs_adj = json_graph.adjacency_data(ug)

with open('last24h/static/last24h/q/q_'+ strin +'_nl.json', 'w+') as fp:
    json.dump(ug_cs_nl,fp)
    
#with open('ug_tree.json', 'w') as fp:
 #   json.dumps(json_ug, fp)
    
#with open('last24h/static/last24h/q/q_'+ strin +'_adj.json', 'w+') as fp:
 #   json.dump(ug_cs_adj, fp)
    