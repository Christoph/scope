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
n = 100
count_suggest = 1
count_comp = 1
comp_count = 0
#create a list of all cliques in all the comps, assign weight to each of them given by the size of the comp weighted inversely by numbering the cluster.


#only leave large clusters
#informaiton: time, comp, clique?

big_list = []
keywords_in = ['ms','.','cookies','cookie','mr','_','-','2016']
graphs = sorted(nx.connected_component_subgraphs(ug), key = len, reverse = True)
for comp in graphs:
    if len(comp) >= 4:
	    timespartition = sorted(list(set([ug.node[i]['time'] for i in comp.nodes() if ug.node[i]['time'] != None])))
	    first_time = timespartition[0]
	    last_time = timespartition[-1]
	    onlytimes = []
	    for a in timespartition:
	       onlytimes.append([i for i in comp.nodes() if ug.node[i]['time'] == a])
	    if first_time != last_time:
	        time_span = (last_time - first_time).total_seconds()
	    else:
	        time_span = 1
	    notime = [ug.node[i]['time'] for i in comp.nodes() if ug.node[i]['time'] == None]
	#if len(comp) > 5:
		#ug.graph['theta'+ str(count_comp)] = comp_count + len(comp)/2
		comp_count += len(comp)
		#tg.add_node(count_comp)


		closeness = nx.closeness_centrality(comp, distance=True)
		all_words = []
		for i in comp:
			ug.node[i]['comp'] = count_comp
			ug.node[i]['single'] = 0
			# compile a list of all words, directly with the weightings. Then merge this big list.
			for j in range(0,2):
				x = sorted(list_corpus[i],key= lambda close:close[1],reverse=True)[j]
				t = sorted([[float(z.split('*"')[0]),z.split('*"')[1].strip('" ')] for z in lsi_model.print_topics(n)[x[0]][1].split('+') if z.split('*"')[1].strip('" ') not in keywords_in],reverse=True)
				s = [[a*x[1],b] for a,b in t] #weigh every word weight by topic weight
				for item in s:
					all_words.append(item)	

		one_word = []
		for a in list(set([b for c,b in all_words if b not in keywords_in])):
			f = [[x,y] for x,y in all_words if y==a]
			one_word.append([sum([x for x,y in f]),a])
		a = sorted(one_word,reverse=True)
		
		#before here you need to convert all the times into isoformat
		if len(notime) == len(comp): #none of the nodes has a timestamp
			time_disclaim = 'no timestamp for this cluster'
			timeinf = ['','','','','']
		elif time_span = 1: #all of those nodes that have a timestamp have the same one
			time_disclaim = 'no timestamp'
			timeinf = ['','',ug.node[i]['time'],'','']
		else: 
			time_disclaim = 'no timestamp'
			t_hours = time_span/3600
			tt1 = str(3*t_hours/4/24) + 'd ' + str(3*t_hours/4%24) + 'h'
			tt2 = str(t_hours/2/24) + 'd ' + str(t_hours/2%24) + 'h'
			tt3 = str(t_hours/4/24) + 'd ' + str(t_hours/4%24) + 'h'
			tt4 = str(t_hours/24) + 'd ' + str(t_hours%24) + 'h'
			timeinf = ['now',tt1,tt2,tt3,tt4]


		if nx.average_clustering(comp) == 1:
			clustering = 100
		else: clustering=str(nx.average_clustering(comp))[2:4]
		if len(a) != 0:
			keywords = [a[0][1], a[1][1]]
			keywords_in.append(keywords[0])
			keywords_in.append(keywords[1])
		else: keywords = ''
		tg.add_node(count_comp, clustering=clustering,name=keywords, timeinf = timeinf, time_disclaim = time_disclaim)	
		tg.add_edge(0,count_comp)

#decide how many topics you want to have printed: for the comp just take only the first two.
	if len(comp) > 5:
		count_clique=1
		clique_count= 0
		for k in sorted(list(nx.find_cliques(comp)),key = len, reverse=True):
			if len(k) >= 3:
				susvec = sorted([[closeness[r],r] for r in k], reverse=True)[0][1]
				if count_clique == 1:
					ug.node[susvec]['keywords'] = keywords
					#hier wird's ein Problem geben, weil noch gar nicht klar ist, welche cliquen es gibt...
				all_words = []
				for j in k:
					# compile a list of all words, directly with the weightings. Then merge this big list.
					for l in range(0,4):
						x = sorted(list_corpus[j],key= lambda close:close[1],reverse=True)[l]
						t = sorted([[float(i.split('*"')[0]),i.split('*"')[1].strip('" ')] for i in lsi_model.print_topics(n)[x[0]][1].split('+') if i.split('*"')[1].strip('" ') not in keywords_in],reverse=True)
						s = [[a*x[1],b] for a,b in t] #weigh every word weight by topic weight
						for item in s:
							all_words.append(item)

				one_word = []
				for a in list(set([b for c,b in all_words if b not in keywords_in])):
					f = [[x,y] for x,y in all_words if y==a]
					one_word.append([sum([x for x,y in f]),a])
				a = sorted(one_word,reverse=True)
				

			

				# tops = []
				
				# for i in range(0,2):
				# tops.append(sorted(list_corpus[m[1]],key= lambda close:close[1],reverse=True)[i])
				# #prop_o = int(math.floor(3./((tops[1][1]/tops[0][1])+1)))#1->1, 2->1,3->0,0.5->2, 0.3->3
				# keyword = []
				# t = sorted([[float(i.split('*"')[0]),i.split('*"')[1].strip('" ')] for i in lsi_model.print_topics(n)[tops[0][0]][1].split('+') if i.split('*"')[1].strip('" ') not in keywords_in],reverse=True)
				# if (len(t) != 0)and(t[0][0]>=0):
				# 	keyword.append(t[0][1])
				# 	keywords_in.append(t[0][1])                          
				# t = sorted([[float(i.split('*"')[0]),i.split('*"')[1].strip('" ')] for i in lsi_model.print_topics(n)[tops[1][0]][1].split('+') if i.split('*"')[1].strip('" ') not in keywords_in],reverse=True)
				# if (len(t) != 0)and(t[0][0]>=0):
				# 	keyword.append(t[0][1])
				# 	keywords_in.append(t[0][1])
				clique_count += len(k)
				big_list.append([len(comp)*len(k)/count_clique,susvec])
				if len(a) == 1:
					keywords = [a[0][1]]
					ug.node[susvec]['keywords'] = keywords
					keywords_in.append(keywords[0])
					tg.add_node(count_comp*100+count_clique-1, size=len(k),name=keywords)
				elif len(a) == 2:
					keywords = [a[0][1], a[1][1]]
					ug.node[susvec]['keywords'] = keywords
					keywords_in.append(keywords[0])
					keywords_in.append(keywords[1])
					tg.add_node(count_comp*100+count_clique-1, size=len(k),name=keywords)
				else: 
					tg.add_node(count_comp*100+count_clique-1, size=len(k))
				tg.add_edge(count_comp,count_comp*100+count_clique-1)
				
				count_clique += 1
		tg.add_node(count_comp*100+count_clique-1, size=len(comp)-clique_count)
		tg.add_edge(count_comp,count_comp*100+count_clique-1) 	#this last node is the one corresponding to all nodes that are not in any clique, i.e. it is on the level of cliques, not comps
		count_comp += 1

	elif len(comp) in [4,5]:
		
		comp_count += len(comp)
		#tg.add_node(count_comp)
		all_words = []
		for z in comp:
			ug.node[z]['comp'] = count_comp
			ug.node[z]['single'] = 0
			# compile a list of all words, directly with the weightings. Then merge this big list.
			for j in range(0,4):
				x = sorted(list_corpus[z],key= lambda close:close[1],reverse=True)[j]
				t = sorted([[float(i.split('*"')[0]),i.split('*"')[1].strip('" ')] for i in lsi_model.print_topics(n)[x[0]][1].split('+') if i.split('*"')[1].strip('" ') not in keywords_in],reverse=True)
				s = [[a*x[1],b] for a,b in t] #weigh every word weight by topic weight
				for item in s:
					all_words.append(item)

		one_word = []
		for a in list(set([b for c,b in all_words if b not in keywords_in])):
			f = [[x,y] for x,y in all_words if y==a]
			one_word.append([sum([x for x,y in f]),a])
		a = sorted(one_word,reverse=True)
		if len(a) != 0:
			keywords = [a[0][1], a[1][1]]
			keywords_in.append(keywords[0])
			keywords_in.append(keywords[1])
			tg.add_node(count_comp*100, size=len(comp),name=keywords)
		else: 
			tg.add_node(count_comp*100, size=len(comp))
		susvec = sorted(closeness.items(), key = lambda close:close[1],reverse=True)[0][0]                
		big_list.append([len(comp)^2,susvec])
		#tg.add_node(count_comp)
		if len(notime) == len(comp): #none of the nodes has a timestamp
			time_disclaim = 'no timestamp for this cluster'
			timeinf = ['','','','','']
		elif time_span = 1: #all of those nodes that have a timestamp have the same one
			time_disclaim = 'no timestamp'
			timeinf = ['','',ug.node[i]['time'],'','']
		else: 
			time_disclaim = 'no timestamp'
			t_hours = time_span/3600
			tt1 = str(3*t_hours/4/24) + 'd ' + str(3*t_hours/4%24) + 'h'
			tt2 = str(t_hours/2/24) + 'd ' + str(t_hours/2%24) + 'h'
			tt3 = str(t_hours/4/24) + 'd ' + str(t_hours/4%24) + 'h'
			tt4 = str(t_hours/24) + 'd ' + str(t_hours%24) + 'h'
			timeinf = ['now',tt1,tt2,tt3,tt4]

		if nx.average_clustering(comp) == 1:
			tg.add_node(count_comp, clustering=100)#)str(nx.average_clustering(comp))[2:4])
		else:
			tg.add_node(count_comp, clustering=str(nx.average_clustering(comp))[2:4])
		tg.add_edge(0,count_comp)		
		tg.add_edge(count_comp,count_comp*100)

		

	else: 
		ug.remove_nodes_from(comp)
	


#split up the keyword finding and the suggestion weighing, add keywords to all susvec for all cliques (you never know...): To find the keywords for a given set of nodes: Extract the first two keywords for each node and then count them by frequency, or accumulated weight? 


maxcount = 15
suggestions = []
for m in sorted(big_list,reverse=True):
	if ((False not in [ug.node[k]['suggest'] == 0 for k in ug.neighbors(m[1])]) and (ug.node[m[1]]['suggest'] == 0))and (len(list_corpus[m[1]]) > 1):
		# tops = []
		
		# for i in range(0,2):
		# 	tops.append(sorted(list_corpus[m[1]],key= lambda close:close[1],reverse=True)[i])
		# 			#prop_o = int(math.floor(3./((tops[1][1]/tops[0][1])+1)))#1->1, 2->1,3->0,0.5->2, 0.3->3
		# keyword = []
		# t = sorted([[float(i.split('*"')[0]),i.split('*"')[1].strip('" ')] for i in lsi_model.print_topics(n)[tops[0][0]][1].split('+') if i.split('*"')[1].strip('" ') not in keywords_in],reverse=True)
		# if (len(t) != 0)and(t[0][0]>=0):
		# 	keyword.append(t[0][1])
		# 	keywords_in.append(t[0][1])                          
		# t = sorted([[float(i.split('*"')[0]),i.split('*"')[1].strip('" ')] for i in lsi_model.print_topics(n)[tops[1][0]][1].split('+') if i.split('*"')[1].strip('" ') not in keywords_in],reverse=True)
		# if (len(t) != 0)and(t[0][0]>=0):
		# 	keyword.append(t[0][1])
		# 	keywords_in.append(t[0][1])
						
		# ug.node[m[1]]['keywords'] = keyword
		ug.node[m[1]]['suggest'] = count_suggest
		
		


		if count_suggest <= maxcount:
			q = Suggest(custom= 'last24h', title = ug.node[m[1]]['title'], url = ug.node[m[1]]['url'], distance = count_suggest, images = ug.node[m[1]]['images'])
			q.save()

		suggestions.append(ug.node[m[1]]['title'])
		count_suggest += 1                                      



#for i in range(1,count_comp-1):

	#tg.node[i]['name']= sorted(d['keywords'] for n,d in ug.nodes_iter(data=True) if d['comp']==i)[0]


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
