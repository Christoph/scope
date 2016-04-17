import networkx as nx
import gensim
import nltk
import re
import string
import json
import urllib
from networkx.readwrite import json_graph

from last24h.models import Suggest

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
#suggestions = Suggest.objects.filter(custom = 'last24h') 
#suggestions.delete()


n = 100
count_suggest = 1
count_comp = 1
big_list = []
small_list = []
keywords_in = ['ms','.','cookies','cookie','mr','_','-','2016']

graphs = sorted(nx.connected_component_subgraphs(ug),key=len,reverse=True)
graphx = sorted([[len(i), nx.average_clustering(i),i] for i in graphs],reverse=True)

for a in graphx:
	comp = a[2]
	if len(comp) >= 4:
		# first take care of the time signatures of the articles for the detail view
		timespartition = sorted(list(set([ug.node[i]['time'] for i in comp.nodes() if ug.node[i]['time'] != None]))) #collect the different times occuring 
		first_time = timespartition[0]
		last_time = timespartition[-1]
		onlytimes = []
		for a in timespartition:
		   onlytimes.append([i for i in comp.nodes() if ug.node[i]['time'] == a]) # partition the set of times into articles with the same timestamp
		if first_time != last_time: #in case they're all published at the same time
			time_span = (last_time - first_time).total_seconds()
		else:
			time_span = 1
		#calculate positions on circle, reserving at least 355-5 deg for ones without timestamp.
		notime = [ug.node[i]['time'] for i in comp.nodes() if ug.node[i]['time'] == None]
		ratio = len(notime)/len(comp)
		notime_count = 1
		#take care of positioning of articles with the same timestamp
		for a in onlytimes:
			relcount = 0
			for i in a:
				if len(a) > 1:
					ug.node[i]['time_pos'] = (ug.node[i]['time'] - last_time).total_seconds()/time_span*350*(1-ratio) + 5 + ratio*175 + relcount/(len(a)-1)*3-3*len(a)/2
					relcount += 1
				else:  
					ug.node[i]['time_pos'] = (ug.node[i]['time'] - last_time).total_seconds()/time_span*350*(1-ratio) + 5 + ratio*175
				#translate into isoformat for display
				ug.node[i]['time'] = ug.node[i]['time'].isoformat()


		#display formatting of time
		if len(notime) == len(comp): #none of the nodes has a timestamp
			time_disclaim = 'no timestamp for this cluster'
			timeinf = ['','','','','']
		elif time_span == 1: #all of those nodes that have a timestamp have the same one
			time_disclaim = 'no timestamp'
			tt0 = ug.node[i]['time']
			timeinf = ['','',tt0[5:7] + '/' + tt0[8:10] + ' ' + tt0[11:16],'','']
		else: 
			time_disclaim = 'no timestamp'
			t_hours = time_span/3600
			if int(3*t_hours/4/24) == 0:
				tt1 = str(int(3*t_hours/4%24)) + 'h'
			else:
				tt1 = str(int(3*t_hours/4/24)) + 'd ' + str(int(3*t_hours/2%24)) + 'h'
			if int(t_hours/2/24) == 0:
				tt2 = str(int(t_hours/2%24)) + 'h'
			else:
				tt2 = str(int(t_hours/2/24)) + 'd ' + str(int(t_hours/2%24)) + 'h'
			if int(t_hours/4/24) == 0:
				tt3 = str(int(t_hours/4%24)) + 'h'
			else:
				tt3 = str(int(t_hours/4/24)) + 'd ' + str(int(t_hours/4%24)) + 'h'
			if int(t_hours/24) == 0:
				tt4 = str(int(t_hours%24)) + 'h'
			else:
				tt4 = str(int(t_hours/24)) + 'd ' + str(int(t_hours%24)) + 'h'
			timeinf = ['now',tt1,tt2,tt3,tt4]

		#now for comp level keyword extraction
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

		if len(a) != 0:
			keywords = [a[0][1], a[1][1]]
			keywords_in.append(keywords[0])
			keywords_in.append(keywords[1])
		else: keywords = ''

		#clustering for detail view
		if nx.average_clustering(comp) == 1:
			clustering = 100
		else: clustering=str(nx.average_clustering(comp))[2:4]
		
		#add the nodes for the arc
		tg.add_node(count_comp, clustering=clustering,name=keywords, timeinf = timeinf, time_disclaim = time_disclaim)  
		tg.add_edge(0,count_comp)

		#suggestion extraction
	if len(comp) > 5:
		count_clique=1
		clique_count= 0
		closeness = nx.closeness_centrality(comp, distance=True)

		for k in sorted(list(nx.find_cliques(comp)),key = len, reverse=True):
			if len(k) >= 3:
				
				susvec = sorted([[closeness[r],r] for r in k], reverse=True)[0][1]
				if count_clique == 1:
					ug.node[susvec]['suggest'] = count_comp
					q = Suggest(custom= 'last24h', title = ug.node[susvec]['title'], url = ug.node[susvec]['url'], distance = count_comp, images = ug.node[susvec]['images'])
					q.save()
				else:
					small_list.append([len(comp)*len(k)/count_clique,susvec])
				#clique level keyword extraction
				all_words = []
				for j in k:
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
				

				if len(a) == 1:
					keywords = [a[0][1]]
					ug.node[susvec]['keywords'] = keywords
					keywords_in.append(keywords[0])
				elif len(a) == 2:
					keywords = [a[0][1], a[1][1]]
					ug.node[susvec]['keywords'] = keywords
					keywords_in.append(keywords[0])
					keywords_in.append(keywords[1])
					
				else:
					keywords = ''

				tg.add_node(count_comp*100+count_clique-1, size=len(k),name=keywords)
				tg.add_edge(count_comp,count_comp*100+count_clique-1)
				clique_count += len(k)
				count_clique += 1
		tg.add_node(count_comp*100+count_clique-1, size=len(comp)-clique_count)
		tg.add_edge(count_comp,count_comp*100+count_clique-1)   #this last node is the one corresponding to all nodes that are not in any clique, i.e. it is on the level of cliques, not comps
		count_comp += 1

	elif len(comp) in [4,5]:
		susvec = sorted(closeness.items(), key = lambda close:close[1],reverse=True)[0][0]   
		ug.node[susvec]['suggest'] = count_comp
		q = Suggest(custom= 'last24h', title = ug.node[susvec]['title'], url = ug.node[susvec]['url'], distance = count_suggest, images = ug.node[susvec]['images'])
		q.save()
		tg.add_node(count_comp*100, size=len(comp))
		tg.add_edge(count_comp,count_comp*100)
		count_comp += 1
	else:

		ug.remove_nodes_from(comp)
	
	
tg.node[0]['final_size']=len(ug.nodes())
tg.node[0]['comps'] = count_comp-1
ug.graph['size']=len(ug.nodes())
ug.graph['comps'] = count_comp-1


#at first there should be an article for every survining comp, then we fill up via biglist. 

#suggestions for database
maxcount = 15
count_suggest = count_comp-1
for m in sorted(small_list,reverse=True):
	if count_suggest <= maxcount:
		if ((False not in [ug.node[k]['suggest'] == 0 for k in ug.neighbors(m[1])]) and (ug.node[m[1]]['suggest'] == 0))and (len(list_corpus[m[1]]) > 1):
			ug.node[susvec]['suggest'] = count_suggest
			q = Suggest(custom= 'last24h', title = ug.node[m[1]]['title'], url = ug.node[m[1]]['url'], distance = count_suggest, images = ug.node[m[1]]['images'])
			q.save()
			count_suggest += 1                                      


#export
from networkx.readwrite import json_graph
ug_nl = json_graph.node_link_data(ug)
tgt = json_graph.tree_data(tg,root=0)
with open('last24h/static/last24h/tgt_cluster.json', 'w') as fp:
	json.dump(tgt,fp)   
with open('last24h/static/last24h/ug_nl_cluster.json', 'w') as fp:
	json.dump(ug_nl,fp)

#send_mail('successful update', 'Successful update. headlines are:' , 'grphtcontact@gmail.com', ['pvboes@gmail.com'])
