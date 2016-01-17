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
import untangle
#import sys
import json
import threading 
import Queue
import time

from last24h.models import Suggest, Alert
 
# Determine scources and mode of extraction


#mode = raw_input("Enter 0 for a search query and 1 for a map")

#Via Googlefeed
articles = []
size = 100
for topic in topics:
#topic = raw_input("Which topic would you like to read about?")

#topic = topic.lower()
#topic = topic.replace(" ","_")
    d = feedparser.parse('https://news.google.co.uk/news/feeds?pz=1&cf=all&ned=en&hl=en&q=' + topic + '&output=rss&num=' + str(size))

    for i in range(0, size-1):
        dd = Article(d.entries[i].link.split('url=')[1], language='en', fetch_images = False, MAX_SUMMARY = 1000)
        articles.append(dd)

#Threading stuff

#from last24h.mthreading import myThread, process_data
exitFlag = 0

global exitFlag, workQueue, queueLock

maxthread = 200
if size < maxthread:
    threadlimit = size
else:
    threadlimit = maxthread
        
threadList = []
for i in range(1,threadlimit):
    threadList.append(str(i))

nameList = articles
queueLock = threading.Lock()
workQueue = Queue.Queue(size)
threads = []
threadID = 1

# Create new threads
for tName in threadList:
    thread = myThread(threadID, tName, workQueue)
    thread.start()
    threads.append(thread)
    threadID += 1

# Fill the queue
queueLock.acquire()
for word in nameList:
    workQueue.put(word)
queueLock.release()


# Wait for queue to empty
while not workQueue.empty():
    pass

# Notify threads it's time to exit
exitFlag = 1

# Wait for all threads to complete
for t in threads:
    t.join()
print "Exiting Main Thread"



#Putting together

doc = [ ]
keywords = []
summary = []
titles = []
urls = []
exclude = ['', 'FT.com / Registration / Sign-up','Error','404 Page not found','Page no longer available']

for article in articles:
    if article.title not in exclude:
        doc.append(article.text)
        titles.append(article.title)
        urls.append(article.url)
        summary.append(article.summary)
        keywords.append(article.keywords)
                          
numpy.save("titles",titles)

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

n = len( dict )

corpus_tfidf= tfidf_model[corp]
lsi_model = gensim.models.LsiModel(corpus_tfidf, id2word=dict, num_topics=20) #
index = gensim.similarities.SparseMatrixSimilarity(lsi_model[corpus_tfidf], num_features = 50 )

#lda_model = gensim.models.LdaModel(corpus_tfidf, id2word=dict, num_topics=20) #initialize an LSI transformation
#index2 = gensim.similarities.SparseMatrixSimilarity(lda_model[corpus_tfidf], num_features = 50 )

dict.save('last24h/static/last24h/queries/'+ topic+'.dict')
lsi_model.save('last24h/static/last24h/queries/'+ topic+'.lsi')
#lda_model.save('/tmp/model.lda') 

#load from gensim objects

#dict = gensim.corpora.Dictionary.load('/tmp/news.dict')
#corpus_tfidf = gensim.corpora.MmCorpus('/tmp/corpus_tf.mm')
#corp = gensim.corpora.MmCorpus('/tmp/corpus.mm')
#lsi_model = gensim.models.LsiModel.load('/tmp/model.lsi')
#lda_model = gensim.models.LdaModel.load('/tmp/model.lda')
#titles = numpy.load("titles.npy")


#Begin Graph visualisation

thresh = 0.18 #the higher the thresh, the more critical  
ug = nx.Graph()
for i in range(0, len(corp)):
    ug.add_node(i,title=titles[i],url=urls[i],suggest=0, summary = summary[i],keywords = keywords[i])#,key=keywords[i])

for i in range( 0, len( corpus_tfidf ) ):
  
    sim = index[ lsi_model[ corp [ i ] ] ]
    for j in range( i+1, len( sim ) ):
        dist = (1. - sim[j])/2.
        if dist < thresh:
            ug.add_edge(i,j,{'weight':dist})

#cliques = list(nx.find_cliques(ug))
#closeness = nx.closeness_centrality(ug, distance=True)
suggestions = Suggest.objects.filter(custom = 'us' + topic) 
suggestions.delete()
max_count = 15
count_suggest = 1
graphs = sorted(nx.connected_component_subgraphs(ug), key = len, reverse = True)
for comp in graphs:
    closeness = nx.closeness_centrality(comp, distance=True)
    if len(comp) > 5:
        for i in sorted(list(nx.find_cliques(comp)),key = len, reverse=True):
            if len(i) > 3:
                susvec = sorted([[closeness[r],r] for r in i], reverse=True)[0][1]
                if (False not in [ug.node[n]['suggest'] == 0 for n in ug.neighbors(susvec)]) and (ug.node[susvec]['suggest'] == 0):
                    ug.node[susvec]['suggest'] = count_suggest
                    if count_suggest < max_count:
                        q = Suggest(title = ug.node[susvec]['title'], url = ug.node[susvec]['url'], custom = 'us' + topic, distance = count_suggest,summary = ug.node[susvec]['summary'])
                        q.save()
                    count_suggest += 1
    elif len(comp) in [2,3,4,5]:
        susvec = sorted(closeness.items(), key = lambda close:close[1],reverse=True)[0][0]
        ug.node[susvec]['suggest'] = count_suggest
        if count_suggest < max_count:
                        q = Suggest(title = ug.node[susvec]['title'], url = ug.node[susvec]['url'], custom = 'us' + topic, distance = count_suggest,summary = ug.node[susvec]['summary'])
                        q.save()
        count_suggest += 1
            
    else: 
        ug.node[comp.nodes()[0]]['suggest'] = count_suggest
        if count_suggest < max_count:
                        q = Suggest(title = ug.node[comp.nodes()[0]]['title'], url = ug.node[comp.nodes()[0]]['url'], custom = 'us' + topic, distance = count_suggest,summary = ug.node[comp.nodes()[0]]['summary'])
                        q.save()
        count_suggest += 1

#give_suggestions(ug,15)

from networkx.readwrite import json_graph

ug_nl = json_graph.node_link_data(ug)  
#ug_tree = json_graph.tree_data(ug) #hier soll noch rein, dass der Graph nach Keywords und query sortiert wird: In der Mitte die Query, dann die Keywords und dann die Artikel
ug_adj = json_graph.adjacency_data(ug)

with open('last24h/static/last24h/queries/us'+ alertstring + '_nl.json', 'w+') as fp:
    json.dump(ug_nl,fp)
    
#with open('ug_tree.json', 'w') as fp:
 #   json.dumps(json_ug, fp)
    
with open('last24h/static/last24h/queries/us'+ alertstring +'_ad.json', 'w+') as fp:
    json.dump(ug_adj, fp)