from django.core.management.base import BaseCommand
import time
import urllib
import threading
import Queue
import os
import datetime
import sys
from django.core.mail import send_mail
from last24h.models import Suggest, Alert, Send
from django_cron import CronJobBase, Schedule                     
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
from django.conf import settings


global workQueue, exitFlag, queueLock

class myThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        print "Starting " + self.name
        process_data(self.name, self.q)
        print "Exiting " + self.name

def process_data(threadName, q):
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            data = q.get()
            queueLock.release()
            data.download()
            data.parse()
            data.nlp()
            print " %s processing" % (threadName)
        else:
            queueLock.release()
            print " %s release" % (threadName)
        time.sleep(1)



class Command(BaseCommand):

    def handle(self,*args,**options):
        time_at_beginning = datetime.datetime.now().replace(second = 0, microsecond = 0, minute = 0)
        for job in Send.objects.all():
            entry = [job.email,job.query,job.user,job.string]
            if entry[2] != None:
                address = entry[2].first_name + ' ' + entry[2].last_name
            else:
                address = 'there'
            send_mail('Your latest alert for: ' + entry[1], 'Hi' + address + ',here is the link to your latest alert for your query:' + entry[1] +
 settings.CURRENT_DOMAIN + '/last24h/cs=' + entry[3] +
 'If you have a profile with us, you can edit the alert at any time from your profile. Otherwise click this link to delete the alert:' +
 settings.CURRENT_DOMAIN +'/last24h/d=' + entry[3], 'valentinjohanncaspar@gmail.com', [entry[0]],
 connection=None, html_message='<head><title>'+ settings.CURRENT_NAME + '| maximise relevance, minimise redundancy</title></head><p>Hi '+
 address + ',</p><p>here is the link to your latest grews alert for your query:</p><p><a href="'
 + settings.CURRENT_DOMAIN + '/last24h/cs=' + entry[3] + '" >' + entry[1] +
 '</a></p><p>If you have a profile with us, you can edit the alert at any time from your profile. Otherwise you can delete your alert by clicking <a href="'
 + settings.CURRENT_DOMAIN + '/last24h/d=' + entry[3]+'">here</a>.</p>')
        Send.objects.all().delete()
        delivery_t = datetime.datetime.now().replace(second = 0, microsecond = 0, minute = 0) + datetime.timedelta(hours = 1)
        for alert in Alert.objects.all():
            #send mails to all in to_send
            diff_in_sec = delivery_t - alert.delivery_time.replace(tzinfo = None, minute= 0)
            print int(diff_in_sec.total_seconds()) % alert.frequency
            if (int(diff_in_sec.total_seconds()) % alert.frequency == 0) and (diff_in_sec.total_seconds() > 0) :
                topics = alert.query.split(',')
                for i in range(0, len(topics)):
                    topics[i] = topics[i].strip(' ').lower().replace(" ","_")
                strin = "AND".join(topics) + '_' + delivery_t.isoformat()[:13]
                         

            # Determine scources and mode of extraction


            #mode = raw_input("Enter 0 for a search query and 1 for a map")

            #Via Googlefeed
                articles = []
                #topic = raw_input("Which topic would you like to read about?")
                size = 100
                #topic = topic.lower()
                #topic = topic.replace(" ","_")
                for topic in topics:
                    d = feedparser.parse('http://news.google.co.uk/news/feeds?pz=1&cf=all&ned=en&hl=en&q=' + topic + '&output=rss&num=' + str(size))

                    for i in range(0, size-1):
                        dd = Article(d.entries[i].link.split('url=')[1], language='en', MAX_SUMMARY = 1000)
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
                images = []
                keywords = []
                summary = []
                titles = []
                urls = []
                exclude = ['', 'FT.com / Registration / Sign-up','Error','404 Page not found','Page no longer available','Page not found','Content not found','403 Forbidden']

                for article in articles:
                    if article.title not in exclude:
                        doc.append(article.text)
                        titles.append(article.title)
                        urls.append(article.url)
                        summary.append(article.summary)
                        images.append(article.top_image)

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

                #porter = nltk.stem.porter.PorterStemmer()

                #for i in range( 0, len( term_vec ) ):
                #    for j in range( 0, len( term_vec[ i ] ) ):
                #        term_vec[ i ][ j ] = porter.stem( term_vec[ i ][ j ] )

                #  Convert term vectors into gensim dictionary

                dict = gensim.corpora.Dictionary( term_vec )
                corp = [ ]
                for i in range( 0, len( term_vec ) ):
                    corp.append( dict.doc2bow( term_vec[ i ] ) )

                #  Create TFIDF vectors based on term vectors bag-of-word corpora

                tfidf_model = gensim.models.TfidfModel( corp )

                #  Create pairwise document similarity index

                n = 25

                corpus_tfidf= tfidf_model[corp]
                lsi_model = gensim.models.LsiModel(corpus_tfidf, id2word=dict, num_topics=25) #
                corpus_lsi = lsi_model[corpus_tfidf]
                list_corpus = []
                for doc in corpus_lsi:
                    list_corpus.append(doc)
                index = gensim.similarities.SparseMatrixSimilarity(corpus_lsi, num_features = 25 )

                #lda_model = gensim.models.LdaModel(corpus_tfidf, id2word=dict, num_topics=20) #initialize an LSI transformation
                #index2 = gensim.similarities.SparseMatrixSimilarity(lda_model[corpus_tfidf], num_features = 50 )

                #dict.save('last24h/static/last24h/queries/'+ strin +'.dict')
                #lsi_model.save('last24h/static/last24h/queries/'+ strin+'.lsi')
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
                    ug.add_node(i,title=titles[i],url=urls[i],suggest=0, summary = summary[i],keywords = [], images = images[i], comp = 0)#,key=keywords[i])

                for i in range( 0, len( corpus_tfidf ) ):

                    sim = index[ lsi_model[ corp [ i ] ] ]
                    for j in range( i+1, len( sim ) ):
                        dist = (1. - sim[j])/2.
                        if dist < thresh:
                            ug.add_edge(i,j,{'weight':dist})

                #cliques = list(nx.find_cliques(ug))
                #closeness = nx.closeness_centrality(ug, distance=True)
                suggestions = Suggest.objects.filter(custom = 'cs' + strin) 
                suggestions.delete()
                max_count = 15
                count_suggest = 1
                count_comp = 1
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
                        if count_suggest <= max_count:
                            q = Suggest(title = ug.node[m[1]]['title'], url = ug.node[m[1]]['url'], distance = count_suggest, images = ug.node[m[1]]['images'],custom ='cs' + strin)
                            q.save()
                            count_suggest += 1         

                #give_suggestions(ug,15)

                from networkx.readwrite import json_graph

                ug_nl = json_graph.node_link_data(ug)  
                #ug_tree = json_graph.tree_data(ug) #hier soll noch rein, dass der Graph nach Keywords und query sortiert wird: In der Mitte die Query, dann die Keywords und dann die Artikel
                #ug_adj = json_graph.adjacency_data(ug)

                with open('/home/django/graphite/static/last24h/cs/cs_'+ strin +'_nl.json', 'w+') as fp:
                    json.dump(ug_nl,fp)

                #with open('ug_tree.json', 'w') as fp:
                 #   json.dumps(json_ug, fp)

                #with open('last24h/static/last24h/cs/cs_'+ strin +'_ad.json', 'w+') as fp:
                 #   json.dump(ug_adj, fp)
                q = Send(email = alert.email, query = alert.query, user = alert.user,string = strin)
                q.save()
