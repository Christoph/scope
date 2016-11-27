global exitFlag, workQueue, queueLock, articlenumber


# from django.core.management.base import BaseCommand
import networkx as nx
import gensim
import nltk
import re
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
import email, imaplib, os,sys
import urllib2
import datetime
from datetime import date,timedelta, datetime
from urlparse import urlparse
from eventregistry import *


er = EventRegistry()
q = QueryArticles(lang = 'deu')
# set the date limit of interest
#q.setDateLimit(datetime.date(2014, 4, 16), datetime.date.today())
# find articles mentioning the company Apple
q.addConcept(er.getConceptUri("Volkswagen"))
# return the list of top 30 articles, including the concepts, categories and article image
q.addRequestedResult(RequestArticlesInfo(count = 200, sortBy = "fb",
    returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(concepts = True, categories = True, image = True))))
res = er.execQuery(q)

print str(res)[0:100]
results = res['articles']['results']

with open('last24h/static/commerz/er_vw.txt',"w+") as h:
    json.dump(results,h)


articles_info= []
for i in results:
    tup = tuple([int(j) for j in tuple(i['date'].split('-') + i['time'].split(':'))+(0,1,-1)])
    ha = datetime.datetime.fromtimestamp(mktime(tup))
    articles_info.append([i['url'],ha])


reload(sys)
sys.setdefaultencoding('utf8')

n1 = 5
n2 = 15

# import csv
# with open("last24h/static/commerz/urls_vw.csv","rb") as f:
# 	reader = csv.reader(f)
# 	article_list = list(reader)

articles = []

for article in articles_info:

	articles.append(Article(article[0],language="de"))



if len(articles) != 0:
    articlenumber = len(articles)
else:
    articlenumber = 1
upper = min(600, len(articles))

# for a in articles:
#     a.download()
#     a.parse()
    
# print "Start threading"

# #Threading stuff

exitFlag = 0

exitFlag = 0
counter = 1
class myThread (threading.Thread):
	def __init__(self, threadID, name, q):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.q = q
	def run(self):
		print "Starting " + self.name
		process_data(self.name, self.q)
		# current_task.update_state(state='DOWNLOAD',
		# meta={'current': 10 + int(counter/articlenumber)*50, 'articles':articlenumber, 'words':0})
		# counter += 1
		# print "Exiting " + self.name

def process_data(threadName, q):
	while not exitFlag:
		queueLock.acquire()
		if not workQueue.empty():
			data = q.get()
			queueLock.release()
			data.download()
			data.parse()
			print " %s processing" % (threadName)
		else:
			queueLock.release()
			print " %s release" % (threadName)
		time.sleep(1)

maxthread = 200
if upper < maxthread:
   threadlimit = upper
else:
   threadlimit = maxthread
        
threadList = []
for i in range(1,threadlimit):
   threadList.append(str(i))

nameList = articles[1:upper]
queueLock = threading.Lock()
workQueue = Queue.Queue(upper)
threads = []
threadID = 1

#Create new threads
for tName in threadList:
   thread = myThread(threadID, tName, workQueue)
   thread.start()
   threads.append(thread)
   threadID += 1

#Fill the queue
queueLock.acquire()
for word in nameList:
   workQueue.put(word)
queueLock.release()


#Wait for queue to empty
while not workQueue.empty():
  pass

#Notify threads it's time to exit
exitFlag = 1

#Wait for all threads to complete
for t in threads:
   t.join()
print "Exiting Main Thread"

#Putting together

doc = [ ]
keywords = []
summary = []
titles = []
urls = []
times = []
images = []
exclude = set(('', 'FT.com / Registration / Sign-up','Error','404 Page not found','Page no longer available', 'File or directory not found','Page not found','Content not found','Seite nicht gefunden','404 :: lr-online'))

unsubscribe_exclude = "If you are not redirected automatically, please click the Unsubscribe button below"

counter = 0
words_total = 0
for i in range(0,upper-1):
    article = articles[i]
    words_total += len(" ".join(article.text))
    if article.title not in exclude and unsubscribe_exclude not in article.text:# and "tech" in article.text:
        doc.append(article.text)
        titles.append(article.title)
        urls.append(article.url)
        images.append(article.top_image)
        times.append(articles_info[i][1])
        summary.append(article.text[0:400] + "...")
        # try:
        #     print article.text
        # except:
        #     pass
        #keywords.append(articles_info[i][2]) 
                            
#        keywords.append(article.keywords)
                          
#Begin Semantic Analysis

#Sentiment Analysis First

import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
 
def word_feats(words2):
    return dict([(word2, True) for word2 in words2])
 
negids = movie_reviews.fileids('neg')
posids = movie_reviews.fileids('pos')
 
negfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'neg') for f in negids]
posfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'pos') for f in posids]
 
negcutoff = len(negfeats)*10/11
poscutoff = len(posfeats)*10/11
 
trainfeats = negfeats[:negcutoff] + posfeats[:poscutoff]
testfeats = negfeats[negcutoff:] + posfeats[poscutoff:]
#print 'train on %d instances, test on %d instances' % (len(trainfeats), len(testfeats))
 
classifier = NaiveBayesClassifier.train(trainfeats)


probs2 = []
for a in doc:
    dist_dict = classifier.prob_classify(word_feats(a.split()))
    probs2.append(dist_dict.prob("pos"))


# print probs2
# print titles
# Remove punctuation, then tokenize documents


punc = re.compile( '[%s]' % re.escape( string.punctuation ) )
term_vec = [ ]

for a in doc:
        a = a.lower()  #these aren't necessary if you're dealing with keywords
        a = punc.sub( '', a )
        term_vec.append( nltk.word_tokenize( a ) )



# Print resulting term vectors

# Remove stop words from term vectors

stop_words = nltk.corpus.stopwords.words( 'german' )

for i in range( 0, len( term_vec ) ):
    term_list = [ ]

    for term in term_vec[ i ]:
        if term not in stop_words:
            term_list.append( term )

    term_vec[ i ] = term_list

# Print term vectors with stop words removed
# stemming is difficult with the keyword extraction ....
    # Porter stem remaining terms

porter = nltk.stem.porter.PorterStemmer()

for i in range( 0, len( term_vec ) ):
  for j in range( 0, len( term_vec[ i ] ) ):
       term_vec[ i ][ j ] = porter.stem( term_vec[ i ][ j ] )

#  Convert term vectors into gensim dictionary

dict = gensim.corpora.Dictionary( term_vec )
corp = [ ]
for i in range( 0, len( term_vec ) ):
    corp.append( dict.doc2bow( term_vec[ i ] ) )

#  Create TFIDF vectors based on term vectors bag-of-word corpora

tfidf_model = gensim.models.TfidfModel( corp )

#  Create pairwise document similarity index


corpus_tfidf= tfidf_model[corp]
lsi_model = gensim.models.LsiModel(corpus_tfidf, id2word=dict, num_topics=n1) #
corpus_lsi = lsi_model[corpus_tfidf]
list_corpus = []
# for dox in corpus_lsi:
#     list_corpus.append(dox)
index = gensim.similarities.SparseMatrixSimilarity(corpus_lsi, num_features = n1 )

#lda_model = gensim.models.LdaModel(corpus_tfidf, id2word=dict, num_topics=20) #initialize an LSI transformation
#index2 = gensim.similarities.SparseMatrixSimilarity(lda_model[corpus_tfidf], num_features = 50 )

gensim.corpora.MmCorpus.serialize('last24h/static/commerz/vw.mm',corp)#/home/django/graphite/static/last24h/l24h.mm', corp)
dict.save('last24h/static/commerz/vw.dict')
lsi_model.save('last24h/static/commerz/vw.lsi')
index.save('last24h/static/commerz/vw.index')
# lda_model.save('/tmp/model.lda') 


#Begin Graph visualisation

#3-articlenumber*0.03/500#0.1/pow(upper/210,2)  #the higher the thresh, the more critical  
ug = nx.Graph()
for i in range(0, len(corp)):
    try:
        source = urlparse(urls[i]).hostname
    except:
        source = "No Source Information"

    # if len(urls[i].split("www.")) != 1:
    #     source = urls[i].split("www.")[1].split("/")[0]
    # elif len(urls[i].split("rss.")) != 1:  
    #     source = urls[i].split("rss.")[1].split("/")[0]
    # else: 
    #     source = urls[i].split("http://")[1].split("/")[0]
    ug.add_node(i,title=titles[i],url=urls[i],suggest=0, summary = summary[i],images = images[i], comp = 0,source= source,keywords='',sent =probs2[i],time = times[i])#,keywords=keywords[i])

graphs = []
score_new = 0
best_thresh = 0.
best_score = 0
#thresh = 0.02

orignumber = len(ug)

lsi_model2 = gensim.models.LsiModel(corpus_tfidf, id2word=dict, num_topics=n2) #
corpus_lsi2 = lsi_model2[corpus_tfidf]
# list_corpus = []
# for dox in corpus_lsi:
#     list_corpus.append(dox)
index2 = gensim.similarities.SparseMatrixSimilarity(corpus_lsi, num_features = n2 )

best_thresh = 0.
best_score = 0#[0,0]




# #Begin Graph visualisation
# thresh = 0.13-articlenumber*0.03/500#+float(pow(articlenumber-500,6))/(float(pow(500,6))*10)#0.15#0.1/pow(upper/210,2)  #the higher the thresh, the less critical  
# ug = nx.Graph()
# for i in range(0, len(corp)):
#     if len(urls[i].split("www.")) != 1:
#         source = urls[i].split("www.")[1].split("/")[0]
#     elif len(urls[i].split("rss.")) != 1:  
#         source = urls[i].split("rss.")[1].split("/")[0]
#     else: 
#         source = urls[i].split("http://")[1].split("/")[0]
#     ug.add_node(i,title=titles[i],url=urls[i],suggest=0, summary = summary[i],images = images[i], comp = 0,source= source,keywords='', time = times[i])#,keywords=keywords[i])

# for i in range( 0, len( corpus_tfidf ) ):
  
#     sim = index[ lsi_model[ corp [ i ] ] ]
#     for j in range( i+1, len( sim ) ):
#         dist = (1. - sim[j])/2.
#         if dist < thresh:
#             ug.add_edge(i,j,{'weight':dist})


for s in [x/1000. for x in xrange(0,500)]:


#while score_new >= score_old:#len(graphs) not in [5,6] and any(len(x) <4 for x in graphs):
    ug.remove_edges_from(ug.edges())

    for i in range(0,len( corpus_tfidf )): 
        sim = index2[ lsi_model2[ corp [ i ] ] ]
        for j in range( i+1, len( sim ) ):
            dist = (1. - sim[j])/2.
            if dist < s and j in ug and i in ug:
                ug.add_edge(i,j,{'weight':dist})
    graphs = sorted(nx.connected_component_subgraphs(ug),key=len,reverse=True)

    test = [x for x in graphs if 20> len(x) >= 4]
    exclude = [x.nodes() for x in graphs if x not in test]
    #test2 = [len(x) for x in test]
    if len(test) >= 3:
        score_new = len(test)#len(test[0])+len(test[1])#sum(test2)#len(test)#test2[0]
        #score_new = [len(test),sum(test2)]
    
    #score_new = sum(test2) #[len(test),sum(test2)]
    
    if score_new > best_score and len(test) >= 3:
        best_score = score_new
        best_thresh = s

        #print thresh
        #thresh += 0.001
        print s
        print len(graphs)
        # for i in graphs:
        #     for ii in i:
        #         print ug.node[ii]['title']
        #     print "and"
        #print test2
        print score_new
        print best_thresh
        # if thresh >= 0.5:
        #     break

 
dispersion = str((1.-2*best_thresh)*100)[:-2] + '%'
print best_thresh
ug.remove_edges_from(ug.edges())
for i in range( 0, len( corpus_tfidf ) ): 
    sim = index2[ lsi_model2[ corp [ i ] ] ]
    for j in range( i+1, len( sim ) ):
        dist = (1. - sim[j])/2.
        if dist < best_thresh and j in ug and i in ug:
            ug.add_edge(i,j,{'weight':dist})
graphs = sorted(nx.connected_component_subgraphs(ug),key=len,reverse=True)
test = [x for x in graphs if 20> len(x) >= 3]
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
size= len(corp)

tg = nx.DiGraph()
tg.add_node(0,overall_size=size)


gg = nx.DiGraph()
gg.add_node(0,overall_size=size)

count_suggest = 1
count_comp = 1
big_list = []
small_list = []
keywords_in = ['ms','.','cookies','cookie','mr','_','-','2016']


graphx = sorted([[len(i), nx.average_clustering(i),i] for i in test],reverse=True)#0:min(5,len(graphs)-1)]
# for i in range(min(6,len(graphs))):
#     ug.remove_nodes_from(graphs[i])

#strin = "rene" + date.today().isoformat()

for a in graphx:
    comp = a[2]
    if len(comp) >= 3:
        # first take care of the time signatures of the articles for the detail view
        timespartition = sorted(list(set([ug.node[i]['time'] for i in comp.nodes() if ug.node[i]['time'] != None]))) #collect the different times occuring 
        if len(timespartition) != 0:
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


            gg.add_node(count_comp,size=len(comp))
            gg.add_edge(0,count_comp)


            time_bins = time_span/20.
            for i in range(0,19):
                lowerbound = first_time.total_seconds() + i*time_bins
                upperbound = first_time.total_seconds() + (i+1)*time_bins
                matching_articles = [k for k in comp if (lowerbound <= ug.node[k]['time'].total_seconds() <= upperbound)]
                gg.add_node(count_comp*100 + i,x=i,y=len(matching_articles))
                gg.add_edge(count_comp,count_comp*100 + i)



            for a in onlytimes:
                relcount = 0
                for i in a:
                    if len(a) > 1:
                        ug.node[i]['time_pos'] = (last_time - ug.node[i]['time']).total_seconds()/time_span*350*(1-ratio) + 5 + ratio*175 + relcount/(len(a)-1)*5-5*len(a)/2
                        relcount += 1
                    else:  
                        ug.node[i]['time_pos'] = (last_time - ug.node[i]['time']).total_seconds()/time_span*350*(1-ratio) + 5 + ratio*175
                    #translate into isoformat for display



            #display formatting of time
            if len(notime) == len(comp): #none of the nodes has a timestamp
                time_disclaim = 'no timestamp for this cluster'
                timeinf = ['','','','','']
            elif time_span == 1: #all of those nodes that have a timestamp have the same one
                time_disclaim = 'no timestamp'
                timeinf = ['','',ug.node[i]['time'].isoformat(),'','']
            else: 
                now = datetime.datetime.now().isoformat()
                now = now[5:7] + '/' + now[8:10] + ' ' + now[11:13] + 'h <br>(GMT)'
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
        else: 
            timeinf = "no time information"
            time_disclaim = "no time information"
        #now for comp level keyword extraction
        #if len(comp) >= 7:
        all_words = []
        for i in comp:
            ug.node[i]['comp'] = count_comp
            ug.node[i]['single'] = 0
            for word in punc.sub('',ug.node[i]['title']).split(" "):
                #print word
                if word not in stop_words:
                    all_words.append(word)
        a = sorted([[len([b for b in all_words if b == word]),word] for word in list(set(all_words))],reverse=True)
        if len(a) >= 2:
                keywords = a[0][1] + ", " + a[1][1]
        elif len(a) == 1:
            keywords = a[0][1]
                #keywords_in.append(keywords[0])
                #keywords_in.append(keywords[1])
        else: 
            keywords = ''

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
        ordering = sorted(closeness.items(), key = lambda close:close[1],reverse=True)
        susvec = ordering[0][0]
        cnode = ug.node[susvec]
        cnode['suggest'] = count_comp
        # q = Suggest(custom= strin, title = ug.node[susvec]['title'], url = ug.node[susvec]['url'], distance = count_comp, images = ug.node[susvec]['images'], keywords = keywords,source=ug.node[susvec]['source'])
        # q.save()

                #add the nodes for the arc
        tg.add_node(count_comp, clustering=clustering,name=keywords)  
        tg.add_edge(0,count_comp)         

        tg.add_node(count_comp*100, size=len(comp))
        tg.add_edge(count_comp,count_comp*100)

        gg.node[count_comp]['name'] = keywords
        #create an array with the number of articles per time bin.

        count_comp += 1
    else:
        ug.remove_nodes_from(comp)


#Here the bit for the overall graphic:
# We bin the overall time scale into twenty equally sized bits. Then, for each of the bins, we check for the number of articles in every comp that appear in this period. Then we create a directed tree graph in which, for every cluster, for every slice the number of articles in that period is the y-component.

for i in ug.nodes():
    try: 
        ug.node[i]['time'] = ug.node[i]['time'].isoformat()
    except:
        ug.node[i]['time'] = ''



tg.add_edge(0,50)
tg.add_node(5000, size= 0.1)
tg.add_edge(50,5000)
tg.node[0]['final_size']=len(ug.nodes())
tg.node[0]['comps'] = count_comp-1
#tg.node[0]['thresh'] = best_thresh
#tg2.node[0]['final_size']=len(ug.nodes())
tg.node[0]['comps'] = count_comp-1
#tg2.node[0]['thresh'] = best_thresh
ug.graph['size']=len(ug.nodes())
ug.graph['comps'] = count_comp-1
# ug.graph['senders'] = senders
ug.graph['thresh'] = best_thresh
# ug.graph['dispersion'] = dispersion
# ug.graph['tech-nontech-ratio'] = str(tech_ratio)#str(len(doc)/float(articlenumber))#
# ug.graph['wordcount'] = str(words)
# ug.graph['links'] = str(no_urls)
ug.graph['articlenumber'] = str(articlenumber)

#export
from networkx.readwrite import json_graph
ug_nl = json_graph.node_link_data(ug)
tgt = json_graph.tree_data(tg,root=0)
ggg = json_graph.tree_data(gg,root=0)
#tgt_mobile = json_graph.tree_data(tg2,root=0)
with open('last24h/static/commerz/tgt_vw.json', 'w+') as fp:
# with open('last24h/static/commerz/tgt_vw.json', 'w+') as fp:
    json.dump(tgt,fp)

with open('last24h/static/commerz/ggg_vw.json', 'w+') as fp:
# with open('last24h/static/commerz/tgt_vw.json', 'w+') as fp:
    json.dump(ggg,fp)
# with open('last24h/static/last24h/cs/cs_'+ strin +'_tgt_mobile.json', 'w+') as fp:
#     json.dump(tgt_mobile,fp)
with open('last24h/static/commerz/ug_vw.json', 'w+') as fp:
# with open('last24h/static/commerz/ug_vw.json', 'w+') as fp:
    json.dump(ug_nl,fp)

#send_mail('successful update', 'Successful update. headlines are:' , 'grphtcontact@gmail.com', ['pvboes@gmail.com'])

