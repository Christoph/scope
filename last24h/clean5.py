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

from last24h.models import Suggest

def give_suggestions(graph,maxcount,filt= None):
    print str(maxcount) + ' Articles ordered by maximal relevance and maximal overlap with neighbours:'
    sug = sorted([[d['suggest'],n] for n,d in graph.nodes_iter(data=True)])
    open('suggestions_today.txt', 'w')
    
   
    for i in range (0, maxcount):
        
        print graph.node[sug[i][1]]['title']
        
def db_suggestions(graph,maxcount,filt= None):
    
    sug = sorted([[d['suggest'],n] for n,d in graph.nodes_iter(data=True)])
    for i in range (0, maxcount):
        q = Suggest(id = i, title = graph.node[sug[i][1]]['title'], url = graph.node[sug[i][1]]['url'], custom = 'None',summary = graph.node[sug[i][1]]['summary'] )
        q.save()


class myThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        #print "Starting " + self.name
        process_data(self.name, self.q)
        #print "Exiting " + self.name

def process_data(threadName, q):
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            data = q.get()
            queueLock.release()
            data.download()
            data.parse()
            #print " %s processing" % (threadName)
        else:
            queueLock.release()
        time.sleep(1)
        
def do_the_thread(upper,articless):
    print "Start threading"
    exitFlag = 0
    maxthread = 200
    print exitFlag
    if upper < maxthread:
        threadlimit = upper
    else:
        threadlimit = maxthread
        
    threadList = []
    for i in range(1,threadlimit):
        threadList.append(str(i))

    nameList = articless[1:upper]
    queueLock = threading.Lock()
    workQueue = Queue.Queue(upper)
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
    return True
        
# Determine scources and mode of extraction

#mode = raw_input("Enter 0 for a search query and 1 for a map")

#Via Googlefeed

feeds = ['http://feeds.guardian.co.uk/theguardian/world/rss','http://www.themoscowtimes.com/rss/top/','http://www.spiegel.de/international/index.rss','http://mondediplo.com/backend','http://www.independent.co.uk/news/rss','http://rss.cnn.com/rss/edition_world.rss','http://feeds.bbci.co.uk/news/rss.xml?edition=int','http://rss.cnn.com/rss/edition.rss','http://feeds.bbci.co.uk/news/technology/rss.xml','http://feeds.bbci.co.uk/news/business/rss.xml','http://www.independent.co.uk/news/world/rss','http://www.nytimes.com/services/xml/rss/nyt/InternationalHome.xml','http://www.economist.com/sections/science-technology/rss.xml','http://www.nytimes.com/services/xml/rss/nyt/InternationalOpinion.xml','http://www.economist.com/sections/international/rss.xml','http://stream.aljazeera.com/stories/feed/rss.xml','http://www.guardian.co.uk/rssfeed/0,,1,00.xml','http://www.aljazeera.com/xml/rss/all.xml']


#fix the fact that now there is no global control on the length of "articles", i.e. the number of articles all together.

articles = []
doc = [ ]
keywords = []
summary = []
titles = []
urls = []
exclude = set(('', 'FT.com / Registration / Sign-up','Error','404 Page not found','Page no longer available', 'File or directory not found'))
non_keywords = set(('World news','Europe','Africa','USA','Technology'))
for feed in feeds:
    articless = []
    d = feedparser.parse(feed)
    for i in range(0, len(d.entries)-1):
        dd = Article(d.entries[i].link, language='en', fetch_images = False)#link.split('url=')[1]
        articless.append(dd)
        articles.append(dd)
    upper = min(600, len(articless))
    do_the_thread(upper,articless)
    counter = 0
    for i in range(0,upper-1):
        article = articless[i]
        if article.title not in exclude:
            doc.append(article.text)
            titles.append(article.title)
            urls.append(article.url)
            if hasattr(d.entries[i],'summary'):
                summary.append(d.entries[i].summary[1:min(200,len(d.entries[i].summary))])
            else:
                summary.append(article.text[1:200])
                               
            if hasattr(d.entries[i],'tags'):
                keywords.append([tag['term'] for tag in d.entries[i].tags if tag['term'] not in non_keywords]) 
            else: 
                keywords.append('')
                            
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
lsi_model = gensim.models.LsiModel(corpus_tfidf, id2word=dict, num_topics=100) #
index = gensim.similarities.SparseMatrixSimilarity(lsi_model[corpus_tfidf], num_features = 100 )

#lda_model = gensim.models.LdaModel(corpus_tfidf, id2word=dict, num_topics=20) #initialize an LSI transformation
#index2 = gensim.similarities.SparseMatrixSimilarity(lda_model[corpus_tfidf], num_features = 50 )

gensim.corpora.MmCorpus.serialize('last24h/static/last24h/l24h.mm', corp)
dict.save('last24h/static/last24h/l24h.dict')
lsi_model.save('last24h/static/last24h/l24h.lsi')
index.save('last24h/static/last24h/l24h.index')
#lda_model.save('/tmp/model.lda') 

#load from gensim objects

#dict = gensim.corpora.Dictionary.load('/tmp/news.dict')
#corpus_tfidf = gensim.corpora.MmCorpus('/tmp/corpus_tf.mm')
#corp = gensim.corpora.MmCorpus('/tmp/corpus.mm')
#lsi_model = gensim.models.LsiModel.load('/tmp/model.lsi')
#lda_model = gensim.models.LdaModel.load('/tmp/model.lda')
#titles = numpy.load("titles.npy")


#Begin Graph visualisation

thresh = 0.15#0.1/pow(upper/210,2)  #the higher the thresh, the more critical  
ug = nx.Graph()
for i in range(0, len(corp)):
    ug.add_node(i,title=titles[i],url=urls[i],suggest=0, summary = summary[i], keywords = keywords[i])#,keywords=keywords[i])

for i in range( 0, len( corpus_tfidf ) ):
  
    sim = index[ lsi_model[ corp [ i ] ] ]
    for j in range( i+1, len( sim ) ):
        dist = (1. - sim[j])/2.
        if dist < thresh:
            ug.add_edge(i,j,{'weight':dist})

#cliques = list(nx.find_cliques(ug))
#closeness = nx.closeness_centrality(ug, distance=True)
maxcount = 15
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
                    if count_suggest <= maxcount:
                        q = Suggest(custom= 'last24h', title = ug.node[susvec]['title'], url = ug.node[susvec]['url'], distance = count_suggest)
                        q.save()
                    count_suggest += 1
    elif len(comp) in [2,3,4,5]:
        susvec = sorted(closeness.items(), key = lambda close:close[1],reverse=True)[0][0]
        ug.node[susvec]['suggest'] = count_suggest
        if count_suggest <= maxcount:
            q = Suggest(custom= 'last24h', title = ug.node[susvec]['title'], url = ug.node[susvec]['url'], distance = count_suggest)
            q.save()
        count_suggest += 1
            
    else: 
        ug.node[comp.nodes()[0]]['suggest'] = count_suggest
        if count_suggest <= maxcount:
            q = Suggest(custom= 'last24h', title = ug.node[susvec]['title'], url = ug.node[susvec]['url'], distance = count_suggest)
            q.save()
        count_suggest += 1

#give_suggestions(ug,15)

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