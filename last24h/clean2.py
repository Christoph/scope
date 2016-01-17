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
from newspaper import news_pool

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


        
# Determine scources and mode of extraction

#Via XML

papers = ['http://www.aljazeera.com']#, 'http://edition.cnn.com', 'http://www.theguardian.com/international', 'http://www.ft.com/home/uk', 'http://www.bbc.com', 'http://www.independent.co.uk', 'http://en.people.cn']
stack = 0.
paperz = []
for paper in papers:
    paperr = newspaper.build(paper, memoize_articles=False)
    paperz.append(paperr)
    stack = stack + paperr.size()

if stack == 0.:
    print "No news articles"
    
news_pool.set(paperz, threads_per_source=200/len(papers)) # (3*2) = 6 threads total
news_pool.join()

doc = [ ]
upper = min(600, stack)
while 1==1:
    keywords = []
    summary = []
    titles = []
    urls = []
    exclude = ['', 'FT.com / Registration / Sign-up','Error','404 Page not found','Page no longer available', 'File or directory not found']
    for paperr in paperz:
        stackper = int(round(upper*(paperr.size()/stack)))
        for i in range(0,stackper):
            if paperr.articles[i].title not in exclude:
                doc.append(paperr.articles[i].text)
                titles.append(paperr.articles[i].title)
                urls.append(paperr.articles[i].url)
                summary.append(paperr.articles[i].text[1:200])

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

    thresh = 0.1/pow(size/210,2)  #the higher the thresh, the more critical  
    ug = nx.Graph()
    for i in range(0, len(corp)):
        ug.add_node(i,title=titles[i],url=urls[i],suggest=0, summary = summary[i])#,keywords=keywords[i])

    for i in range( 0, len( corpus_tfidf ) ):
  
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
                        ug.node[susvec]['suggest'] = count_suggest
                        count_suggest += 1
        elif len(comp) in [2,3,4,5]:
            susvec = sorted(closeness.items(), key = lambda close:close[1],reverse=True)[0][0]
            ug.node[susvec]['suggest'] = count_suggest
            count_suggest += 1
            
        else: 
            ug.node[comp.nodes()[0]]['suggest'] = count_suggest
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