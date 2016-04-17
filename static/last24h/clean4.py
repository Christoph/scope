import networkx as nx
import gensim
import nltk
import re
import string
import numpy
import scipy
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
from django.core.mail import send_mail
from time import mktime
from datetime import datetime
from last24h.models import Suggest
from django.templatetags.static import static

def return_articles(feeds,non_keywords):
	articles_info = []
	for feed in feeds:
		d = feedparser.parse(feed)
		for i in range(0, len(d.entries)-1):
			dd = Article(d.entries[i].link, language='en')#, fetch_images = False)#link.split('url=')[1]
			if hasattr(d.entries[i],'summary'):
				aa = d.entries[i].summary
				if "<div>" in aa:
					aa = aa.split("<div>")[0] + " " + aa.split("<div>")[2]

				ee = aa[0:min(400,len(d.entries[i].summary))]
			else:
				ee = ''
			if hasattr(d.entries[i],'published_parsed'):
				ff = datetime.fromtimestamp(mktime(d.entries[i].published_parsed))
			else:
				ff = None
			articles_info.append([dd,ee,ff])#,ff    
	return articles_info
	
# Determine scources and mode of extraction
			
#Via Googlefeed
articles = []
feeds = ['http://feeds.guardian.co.uk/theguardian/world/rss','http://www.themoscowtimes.com/rss/top/','http://www.spiegel.de/international/index.rss','http://mondediplo.com/backend','http://feeds.bbci.co.uk/news/business/rss.xml','http://www.independent.co.uk/news/world/rss','http://www.nytimes.com/services/xml/rss/nyt/InternationalHome.xml','http://www.aljazeera.com/xml/rss/all.xml','feed://timesofindia.feedsportal.com/c/33039/f/533916/index.rss','http://www.thenation.com/rss/articles','http://feeds.washingtonpost.com/rss/world/asia-pacific','http://www.telegraph.co.uk/finance/economics/rss','feed://www.thejc.com/feed/news','http://feeds.bbci.co.uk/news/technology/rss.xml','feed://www.buenosairesherald.com/articles/rss.aspx','feed://muslimnews.co.uk/feed/?post_type=news','http://www.latimes.com/world/rss2.0.xml','http://feeds.chicagotribune.com/chicagotribune/news','http://feeds.feedburner.com/TheAustralianTheWorld']
 
non_keywords = set(('World news','Europe','Africa','USA','Technology','Approved','Password','Biography'))
articles_info = return_articles(feeds,non_keywords)

articles = [k[0] for k in articles_info]
print len(articles)
upper = min(600, len(articles))

for a in articles:
    a.download()
    a.parse()
	
# print "Start threading"

# #Threading stuff

# exitFlag = 0

# class myThread (threading.Thread):
#    def __init__(self, threadID, name, q):
# 	   threading.Thread.__init__(self)
# 	   self.threadID = threadID
# 	   self.name = name
# 	   self.q = q
#    def run(self):
# 	   #print "Starting " + self.name
# 	   process_data(self.name, self.q)
# 	   #print "Exiting " + self.name

# def process_data(threadName, q):
#    while not exitFlag:
#    	queueLock.acquire()
#    	if not workQueue.empty():
#    		data = q.get()
# 		queueLock.release()
# 		data.download()
# 		data.parse()
# 		  #print " %s processing" % (threadName)
# 	else:
# 		queueLock.release()
# 	time.sleep(1)

# maxthread = 200
# if upper < maxthread:
#    threadlimit = upper
# else:
#    threadlimit = maxthread
		
# threadList = []
# for i in range(1,threadlimit):
#    threadList.append(str(i))

# nameList = articles[1:upper]
# queueLock = threading.Lock()
# workQueue = Queue.Queue(upper)
# threads = []
# threadID = 1

# #Create new threads
# for tName in threadList:
#    thread = myThread(threadID, tName, workQueue)
#    thread.start()
#    threads.append(thread)
#    threadID += 1

# #Fill the queue
# queueLock.acquire()
# for word in nameList:
#    workQueue.put(word)
# queueLock.release()


# #Wait for queue to empty
# while not workQueue.empty():
#   pass

# #Notify threads it's time to exit
# exitFlag = 1

# #Wait for all threads to complete
# for t in threads:
#    t.join()
# print "Exiting Main Thread"

#Putting together

doc = [ ]
keywords = []
summary = []
titles = []
urls = []
times = []
images = []
exclude = set(('', 'FT.com / Registration / Sign-up','Error','404 Page not found','Page no longer available', 'File or directory not found','Page not found','Content not found'))

counter = 0

for i in range(0,upper-1):
	article = articles[i]
	if article.title not in exclude:
		doc.append(article.text)
		titles.append(article.title)
		urls.append(article.url)
		images.append(article.top_image)
		times.append(articles_info[i][2])
		if articles_info[i][1] != '':
			summary.append(articles_info[i][1])
		else: 
			summary.append(article.text[0:400] + "...")
		#keywords.append(articles_info[i][2]) 
							
#        keywords.append(article.keywords)
						  
#Begin Semantic Analysis

# Remove punctuation, then tokenize documents

punc = re.compile( '[%s]' % re.escape( string.punctuation ) )
term_vec = [ ]

for a in doc:
		a = a.lower()  #these aren't necessary if you're dealing with keywords
		a = punc.sub( '', a )
		term_vec.append( nltk.word_tokenize( a ) )

# Print resulting term vectors

# Remove stop words from term vectors

stop_words = nltk.corpus.stopwords.words( 'english' )

for i in range( 0, len( term_vec ) ):
	term_list = [ ]

	for term in term_vec[ i ]:
		if term not in stop_words:
			term_list.append( term )

	term_vec[ i ] = term_list

# Print term vectors with stop words removed
# stemming is difficult with the keyword extraction ....
	# Porter stem remaining terms

#porter = nltk.stem.porter.PorterStemmer()

#for i in range( 0, len( term_vec ) ):
#   for j in range( 0, len( term_vec[ i ] ) ):
#        term_vec[ i ][ j ] = porter.stem( term_vec[ i ][ j ] )

#  Convert term vectors into gensim dictionary

dict = gensim.corpora.Dictionary( term_vec )
corp = [ ]
for i in range( 0, len( term_vec ) ):
	corp.append( dict.doc2bow( term_vec[ i ] ) )

#  Create TFIDF vectors based on term vectors bag-of-word corpora

tfidf_model = gensim.models.TfidfModel( corp )

#  Create pairwise document similarity index

n = 100

corpus_tfidf= tfidf_model[corp]

lsi_model = gensim.models.LsiModel(corpus_tfidf, id2word=dict, num_topics=n) #
corpus_lsi = lsi_model[corpus_tfidf]
list_corpus = []
for dox in corpus_lsi:
	list_corpus.append(dox)
index = gensim.similarities.SparseMatrixSimilarity(corpus_lsi, num_features = n )

#lda_model = gensim.models.LdaModel(corpus_tfidf, id2word=dict, num_topics=20) #initialize an LSI transformation
#index2 = gensim.similarities.SparseMatrixSimilarity(lda_model[corpus_tfidf], num_features = 50 )

gensim.corpora.MmCorpus.serialize('static/last24h/l24h.mm',corp)#/home/django/graphite/static/last24h/l24h.mm', corp)
dict.save('static/last24h/l24h.dict')
lsi_model.save('static/last24h/l24h.lsi')
index.save('static/last24h/l24h.index')
#lda_model.save('/tmp/model.lda') 


#Begin Graph visualisation

thresh = 0.10#0.1/pow(upper/210,2)  #the higher the thresh, the more critical  
ug = nx.Graph()
for i in range(0, len(corp)):
	if len(urls[i].split("www.")) != 1:
		source = urls[i].split("www.")[1].split("/")[0]
	elif len(urls[i].split("rss.")) != 1:  
		source = urls[i].split("rss.")[1].split("/")[0]
	else: 
		source = urls[i].split("http://")[1].split("/")[0]
	ug.add_node(i,title=titles[i],url=urls[i],suggest=0, summary = summary[i],images = images[i], comp = 0,source= source,keywords='', time = times[i])#,keywords=keywords[i])

for i in range( 0, len( corpus_tfidf ) ):
  
	sim = index[ lsi_model[ corp [ i ] ] ]
	for j in range( i+1, len( sim ) ):
		dist = (1. - sim[j])/2.
		if dist < thresh:
			ug.add_edge(i,j,{'weight':dist})

			
suggestions = Suggest.objects.filter(custom = 'last24h') 
suggestions.delete()
			
size= len(corp)
tg = nx.DiGraph()
tg.add_node(0,overall_size=size)


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
					ug.node[i]['time_pos'] = (last_time - ug.node[i]['time']).total_seconds()/time_span*350*(1-ratio) + 5 + ratio*175 + relcount/(len(a)-1)*5-5*len(a)/2
					relcount += 1
				else:  
					ug.node[i]['time_pos'] = (last_time - ug.node[i]['time']).total_seconds()/time_span*350*(1-ratio) + 5 + ratio*175
				#translate into isoformat for display
				ug.node[i]['time'] = ug.node[i]['time'].isoformat()


		#display formatting of time
		if len(notime) == len(comp): #none of the nodes has a timestamp
			time_disclaim = 'no timestamp for this cluster'
			timeinf = ['','','','','']
		elif time_span == 1: #all of those nodes that have a timestamp have the same one
			time_disclaim = 'no timestamp'
			timeinf = ['','',ug.node[i]['time'],'','']
		else: 
			now = datetime.now().isoformat()
			now = now[5:7] + '/' + now[8:10] + ' ' + now[11:13] + 'h'
			time_disclaim = 'no timestamp'
			t_hours = time_span/3600
			if int(t_hours/4/24) == 0:
				tt1 = str(int(t_hours/4%24)) + 'h'
			elif int(t_hours/4%24) == 0:
				tt1 = str(int(t_hours/4/24)) + 'd '
			else:
				tt1 = str(int(t_hours/4/24)) + 'd ' + str(int(t_hours/4%24)) + 'h'
			if int(t_hours/2/24) == 0:
				tt2 = str(int(t_hours/2%24)) + 'h'
			elif int(t_hours/2%24) == 0:
				tt2 = str(int(t_hours/2/24)) + 'd '
			else:
				tt2 = str(int(t_hours/2/24)) + 'd ' + str(int(t_hours/2%24)) + 'h'
			if int(3*t_hours/4/24) == 0:
				tt3 = str(int(3*t_hours/4%24)) + 'h'
			elif int(3*t_hours/4%24) == 0:
				tt3 = str(int(3*t_hours/4/24)) + 'd '
			else:
				tt3 = str(int(3*t_hours/4/24)) + 'd ' + str(int(3*t_hours/4%24)) + 'h'
			if int(t_hours/24) == 0:
				tt4 = str(int(t_hours%24)) + 'h'
			elif int(t_hours/4%24) == 0:
				tt4 = str(int(t_hours/4/24)) + 'd '
			else:
				tt4 = str(int(t_hours/24)) + 'd ' + str(int(t_hours%24)) + 'h'
			timeinf = [now,tt1,tt2,tt3,tt4]

		#now for comp level keyword extraction
		if len(comp) >= 7:
			all_words = []
			for i in comp:
				ug.node[i]['comp'] = count_comp
				ug.node[i]['single'] = 0
				for word in punc.sub('',ug.node[i]['title']).split(" "):
					if word not in stop_words:
						all_words.append(word)
			a = sorted([[len([b for b in all_words if b == word]),word] for word in list(set(all_words))],reverse=True)
			keywords = [a[0][1], a[1][1]]
		else:
			for i in comp:
				ug.node[i]['comp'] = count_comp
				ug.node[i]['single'] = 0
			all_words = []
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
				#keywords_in.append(keywords[0])
				#keywords_in.append(keywords[1])
			else: keywords = ''

		#clustering for detail view
		if nx.average_clustering(comp) == 1:
			clustering = 100
		else: clustering=str(nx.average_clustering(comp))[2:4]
		
		#compute the centrality to turn them into one detail view and the radius size
		count_degree = 1
	#elif len(comp) in [4,5]:
		closeness = nx.closeness_centrality(comp, distance=True)
		#for [b,a] in sorted([[closeness[r],r] for r in comp.nodes()], reverse=True):
		for (a,b) in sorted([[a,nx.degree(comp)[a]] for a in nx.degree(comp)], key= lambda close:close[1], reverse= True):
			ug.node[a]['deg'] = b
			ug.node[a]['deg_pos'] = float(count_degree)/len(comp)*360	
			count_degree += 1
		susvec = sorted(closeness.items(), key = lambda close:close[1],reverse=True)[0][0]   
		ug.node[susvec]['suggest'] = count_comp
		#q = Suggest(custom= 'last24h', title = ug.node[susvec]['title'], url = ug.node[susvec]['url'], distance = count_comp, images = ug.node[susvec]['images'])
		#q.save()


				#add the nodes for the arc
		tg.add_node(count_comp, clustering=clustering,name=keywords, timeinf = timeinf, time_disclaim = time_disclaim)  
		tg.add_edge(0,count_comp)


		tg.add_node(count_comp*100, size=len(comp))
		tg.add_edge(count_comp,count_comp*100)
		count_comp += 1
	else:

		ug.remove_nodes_from(comp)


tg.add_edge(0,50)
tg.add_node(5000, size= 0)
tg.add_edge(50,5000)
tg.node[0]['final_size']=len(ug.nodes())
tg.node[0]['comps'] = count_comp-1
ug.graph['size']=len(ug.nodes())
ug.graph['comps'] = count_comp-1

#export
from networkx.readwrite import json_graph
ug_nl = json_graph.node_link_data(ug)
tgt = json_graph.tree_data(tg,root=0)
with open(settings.STATIC_BREV + static('last24h/tgt_cluster.json'), 'w+') as fp:
    json.dump(tgt,fp)
with open(settings.STATIC_BREV + static('last24h/ug_nl_cluster.json'), 'w+') as fp:
    json.dump(ug_nl,fp)

#send_mail('successful update', 'Successful update. headlines are:' , 'grphtcontact@gmail.com', ['pvboes@gmail.com'])
