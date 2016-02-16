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

dict = gensim.corpora.Dictionary.load('static/last24h/l24h.dict')
corp = gensim.corpora.MmCorpus('static/last24h/l24h.mm')
lsi_model = gensim.models.LsiModel.load('static/last24h/l24h.lsi')
index = gensim.similarities.MatrixSimilarity.load('static/last24h/l24h.index')
#corpus_tfidf = gensim.corpora.MmCorpus('/tmp/corpus_tf.mm')
data = json.loads(open('static/last24h/ug_nl.json').read())
ug = json_graph.node_link_graph(data)

size= len(corp)

tg = nx.DiGraph()
tg.add_node(0,overall_size=size)

#import json graph and assign from another graph


			
#suggestions = Suggest.objects.filter(custom = 'last24h') 
#suggestions.delete()
			
#cliques = list(nx.find_cliques(ug))
#closeness = nx.closeness_centrality(ug, distance=True)

count_suggest = 1
count_comp = 1
comp_count = 0
#create a list of all cliques in all the comps, assign weight to each of them given by the size of the comp weighted inversely by numbering the cluster.


#only leave large clusters
#informaiton: time, comp, clique?

big_list = []
keywords_in = ['ms','.','cookies','cookie','mr','_','-']
graphs = sorted(nx.connected_component_subgraphs(ug), key = len, reverse = True)
for comp in graphs:
	if len(comp) >= 5:
		#ug.graph['theta'+ str(count_comp)] = comp_count + len(comp)/2
		comp_count += len(comp)
		#tg.add_node(count_comp)
		tg.add_node(count_comp, clustering=nx.average_clustering(comp))
		tg.add_edge(0,count_comp)

		closeness = nx.closeness_centrality(comp, distance=True)
		count_clique=1
		clique_count= 0
		for i in comp:
			ug.node[i]['comp'] = count_comp
			ug.node[i]['single'] = 0
		for i in sorted(list(nx.find_cliques(comp)),key = len, reverse=True):
			if len(i) >= 3:
				susvec = sorted([[closeness[r],r] for r in i], reverse=True)[0][1]
				big_list.append([len(comp)*len(i)/count_clique,susvec])
				tg.add_node(count_comp*100+count_clique-1, size=len(i))
				tg.add_edge(count_comp,count_comp*100+count_clique-1)
				clique_count += len(i)
				count_clique += 1
		tg.add_node(count_comp*100+count_clique-1, size=len(comp)-clique_count)
		tg.add_edge(count_comp,count_comp*100+count_clique-1)
		count_comp += 1	
	elif len(comp) in [4,5]:
		for i in comp: 
			ug.node[i]['single'] = 0
		susvec = sorted(closeness.items(), key = lambda close:close[1],reverse=True)[0][0]                
		big_list.append([len(comp)^2,susvec])
		#tg.add_node(count_comp)
		tg.add_node(count_comp*100, size=len(comp))
		tg.add_edge(0,count_comp)		
		tg.add_edge(count_comp,count_comp*100)
		ug.graph['theta'+ str(count_comp)] = comp_count + len(comp)/2
		comp_count += len(comp)
		count_comp += 1
	else: 
		ug.remove_nodes_from(comp)
	


#split up the keyword finding and the suggestion weighing, add keywords to all susvec for all cliques (you never know...): To find the keywords for a given set of nodes: Extract the first two keywords for each node and then count them by frequency, or accumulated weight? 


maxcount = 15
suggestions = []
for m in sorted(big_list,reverse=True):
	if ((False not in [ug.node[k]['suggest'] == 0 for k in ug.neighbors(m[1])]) and (ug.node[m[1]]['suggest'] == 0))and (len(list_corpus[m[1]]) > 1):
		tops = []
		
		for i in range(0,2):
			tops.append(sorted(list_corpus[m[1]],key= lambda close:close[1],reverse=True)[i])
					#prop_o = int(math.floor(3./((tops[1][1]/tops[0][1])+1)))#1->1, 2->1,3->0,0.5->2, 0.3->3
		keyword = []
		t = sorted([[float(i.split('*"')[0]),i.split('*"')[1].strip('" ')] for i in lsi_model.print_topics(n)[tops[0][0]][1].split('+') if i.split('*"')[1].strip('" ') not in keywords_in],reverse=True)
		if (len(t) != 0)and(t[0][0]>=0):
			keyword.append(t[0][1])
			keywords_in.append(t[0][1])                          
		t = sorted([[float(i.split('*"')[0]),i.split('*"')[1].strip('" ')] for i in lsi_model.print_topics(n)[tops[1][0]][1].split('+') if i.split('*"')[1].strip('" ') not in keywords_in],reverse=True)
		if (len(t) != 0)and(t[0][0]>=0):
			keyword.append(t[0][1])
			keywords_in.append(t[0][1])
						
		ug.node[m[1]]['keywords'] = keyword
		ug.node[m[1]]['suggest'] = count_suggest
		
		


		if count_suggest <= maxcount:
			q = Suggest(custom= 'last24h', title = ug.node[m[1]]['title'], url = ug.node[m[1]]['url'], distance = count_suggest, images = ug.node[m[1]]['images'])
			q.save()

		suggestions.append(ug.node[m[1]]['title'])
		count_suggest += 1                                      



for i in range(1,count_comp-1):

	tg.node[i]['name']= sorted(d['keywords'] for n,d in ug.nodes_iter(data=True) if d['comp']==i)[0]


tg.node[0]['final_size']=len(ug.nodes())
ug.graph['size']=len(ug.nodes())

from networkx.readwrite import json_graph


ug_nl = json_graph.node_link_data(ug)
tgt = json_graph.tree_data(tg,root=0)
#ug_tree = json_graph.tree_data(ug) #hier soll noch rein, dass der Graph nach Keywords und query sortiert wird: In der Mitte die Query, dann die Keywords und dann die Artikel
#ug_adj = json_graph.adjacency_data(ug)

with open('last24h/static/last24h/tgt_cluster.json', 'w') as fp:
	json.dump(tgt,fp)
   


with open('last24h/static/last24h/ug_nl_cluster.json', 'w') as fp:
	json.dump(ug_nl,fp)
	
#with open('ug_tree.json', 'w') as fp:
 #   json.dumps(json_ug, fp)
	
#with open('last24h/static/last24h/ug_adj.json', 'w') as fp:
 #   json.dump(ug_adj, fp)

#send_mail('successful update', 'Successful update. headlines are:' , 'grphtcontact@gmail.com', ['pvboes@gmail.com'])
