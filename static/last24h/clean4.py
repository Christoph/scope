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

from last24h.models import Suggest

def return_articles(feeds,non_keywords):
    articles_info = []
    for feed in feeds:
        d = feedparser.parse(feed)
        for i in range(0, len(d.entries)-1):
            dd = Article(d.entries[i].link, language='en')#, fetch_images = False)#link.split('url=')[1]
            if hasattr(d.entries[i],'summary'):
                ee = d.entries[i].summary[0:min(200,len(d.entries[i].summary))]
            else:
                ee = ''
            #  if hasattr(d.entries[i],'tags'):
            #      ff = [tag['term'] for tag in d.entries[i].tags if tag['term'] not in non_keywords] 
            # else: 
            #    ff = ['']
            articles_info.append([dd,ee])#,ff    
    return articles_info
    
# Determine scources and mode of extraction
            
#mode = raw_input("Enter 0 for a search query and 1 for a map")

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
    
#print "Start threading"

#Threading stuff

#exitFlag = 0

#class myThread (threading.Thread):
#    def __init__(self, threadID, name, q):
#        threading.Thread.__init__(self)
#        self.threadID = threadID
#        self.name = name
#        self.q = q
#    def run(self):
#        #print "Starting " + self.name
#        process_data(self.name, self.q)
#        #print "Exiting " + self.name

#def process_data(threadName, q):
#    while not exitFlag:
#       queueLock.acquire()
#      if not workQueue.empty():
#         data = q.get()
    #        queueLock.release()
#            data.download()
 #           data.parse()
#           #print " %s processing" % (threadName)
#        else:
#            queueLock.release()
#       time.sleep(1)

#maxthread = 200
#if upper < maxthread:
 #   threadlimit = upper
#else:
 #   threadlimit = maxthread
        
#threadList = []
#for i in range(1,threadlimit):
#    threadList.append(str(i))

#nameList = articles[1:upper]
#queueLock = threading.Lock()
#workQueue = Queue.Queue(upper)
#threads = []
#threadID = 1

# Create new threads
#for tName in threadList:
#    thread = myThread(threadID, tName, workQueue)
#    thread.start()
#    threads.append(thread)
#   threadID += 1

# Fill the queue
#queueLock.acquire()
#for word in nameList:
#    workQueue.put(word)
#queueLock.release()


# Wait for queue to empty
#while not workQueue.empty():
#   pass

# Notify threads it's time to exit
#exitFlag = 1

# Wait for all threads to complete
#for t in threads:
#    t.join()
#print "Exiting Main Thread"



#Putting together

doc = [ ]
keywords = []
summary = []
titles = []
urls = []
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
        if articles_info[i][1] != '':
            summary.append(articles_info[i][1])
        else: 
            summary.append(article.text[0:200])
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

n = 250

corpus_tfidf= tfidf_model[corp]

lsi_model = gensim.models.LsiModel(corpus_tfidf, id2word=dict, num_topics=n) #
corpus_lsi = lsi_model[corpus_tfidf]
list_corpus = []
for dox in corpus_lsi:
    list_corpus.append(dox)
index = gensim.similarities.SparseMatrixSimilarity(corpus_lsi, num_features = n )

#lda_model = gensim.models.LdaModel(corpus_tfidf, id2word=dict, num_topics=20) #initialize an LSI transformation
#index2 = gensim.similarities.SparseMatrixSimilarity(lda_model[corpus_tfidf], num_features = 50 )

gensim.corpora.MmCorpus.serialize('/home/django/graphite/static/last24h/l24h.mm', corp)
dict.save('/home/django/graphite/static/last24h/l24h.dict')
lsi_model.save('/home/django/graphite/static/last24h/l24h.lsi')
index.save('/home/django/graphite/static/last24h/l24h.index')
#lda_model.save('/tmp/model.lda') 

#load from gensim objects

#dict = gensim.corpora.Dictionary.load('/tmp/news.dict')
#corpus_tfidf = gensim.corpora.MmCorpus('/tmp/corpus_tf.mm')
#corp = gensim.corpora.MmCorpus('/tmp/corpus.mm')
#lsi_model = gensim.models.LsiModel.load('/tmp/model.lsi')
#lda_model = gensim.models.LdaModel.load('/tmp/model.lda')
#titles = numpy.load("titles.npy")

#produce keywords

    #extract for every article the strongest topics, then depending on the weighting the three strongest words, then add these and later make sure only the, otherwise maybe only find the keywords for the suggestions or the cluster kings



#Begin Graph visualisation

thresh = 0.25#0.1/pow(upper/210,2)  #the higher the thresh, the more critical  
ug = nx.Graph()
for i in range(0, len(corp)):
    ug.add_node(i,title=titles[i],url=urls[i],suggest=0, summary = summary[i],images = images[i], comp = 0,keywords='' )#,keywords=keywords[i])

for i in range( 0, len( corpus_tfidf ) ):
  
    sim = index[ lsi_model[ corp [ i ] ] ]
    for j in range( i+1, len( sim ) ):
        dist = (1. - sim[j])/2.
        if dist < thresh:
            ug.add_edge(i,j,{'weight':dist})

            
suggestions = Suggest.objects.filter(custom = 'last24h') 
suggestions.delete()
            
#cliques = list(nx.find_cliques(ug))
#closeness = nx.closeness_centrality(ug, distance=True)
maxcount = 15
count_suggest = 1
count_comp = 1
#create a list of all cliques in all the comps, assign weight to each of them given by the size of the comp weighted inversely by numbering the cluster.

big_list = []
keywords_in = ['ms','.','cookies','cookie','mr','_','-']
graphs = sorted(nx.connected_component_subgraphs(ug), key = len, reverse = True)
for comp in graphs:
    closeness = nx.closeness_centrality(comp, distance=True)
    count_clique=1
    for i in comp: 
        ug.node[i]['comp'] = count_comp
    count_comp += 1    
    if len(comp) > 5:
        for i in comp: 
            ug.node[i]['single'] = 0
        for i in sorted(list(nx.find_cliques(comp)),key = len, reverse=True):
            if len(i) >= 3:
                susvec = sorted([[closeness[r],r] for r in i], reverse=True)[0][1]
                big_list.append([len(comp)*len(i)/count_clique,susvec])
                count_clique += 0
    elif len(comp) in [2,3,4,5]:
        for i in comp: 
            ug.node[i]['single'] = 0
        susvec = sorted(closeness.items(), key = lambda close:close[1],reverse=True)[0][0]                
        big_list.append([len(comp)^2,susvec])
    else: 
        ug.node[comp.nodes()[0]]['single'] = 1
        big_list.append([1,comp.nodes()[0]])
        
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
            
from networkx.readwrite import json_graph

ug_nl = json_graph.node_link_data(ug)  
#ug_tree = json_graph.tree_data(ug) #hier soll noch rein, dass der Graph nach Keywords und query sortiert wird: In der Mitte die Query, dann die Keywords und dann die Artikel
#ug_adj = json_graph.adjacency_data(ug)

with open('static/last24h/ug_nl.json', 'w') as fp:
    json.dump(ug_nl,fp)
    
#with open('ug_tree.json', 'w') as fp:
 #   json.dumps(json_ug, fp)
    
#with open('last24h/static/last24h/ug_adj.json', 'w') as fp:
 #   json.dump(ug_adj, fp)

send_mail('successful update', 'Successful update. headlines are:' , 'grphtcontact@gmail.com', ['pvboes@gmail.com'])
