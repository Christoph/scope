# import networkx as nx
# import gensim
# import nltk
# import re
# import string
# import numpy
# import scipy
# import feedparser
# import newspaper
# from newspaper import Article
# import Queue
# import threading
# import time
# import untangle
# import sys
# import json
# import urllib
# import math
# from django.core.mail import send_mail
# from time import mktime
# from datetime import datetime
# 
# import copy

#from celery import shared_task, current_task


def return_articles(feeds,non_keywords):
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

    import copy

    from celery import shared_task, current_task

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

#feeds = ['http://news.google.co.uk/news/feeds?pz=1&cf=all&ned=en&hl=en&q=' + topic + '&output=rss&num=' + str(size)]
 
non_keywords = set(('World news','Europe','Africa','USA','Technology','Approved','Password','Biography'))
articles_info = return_articles(feeds,non_keywords)


articles = [k[0] for k in articles_info]
if len(articles) != 0:
    articlenumber = len(articles)
else:
    articlenumber = 1
print len(articles)
size = len(articles)
upper = min(600, size)



# for a in articles:
#     a.download()
#     a.parse()
    

#Threading stuff

#from last24h.mthreading import myThread, process_data
exitFlag = 0

global exitFlag, workQueue, queueLock, articlenumber

if alert == 0:
    current_task.update_state(state='DOWNLOAD',
                        meta={'current': 20, 'articles': articlenumber, 'words':0})


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


# Fill the queue


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
 
numpy.save("titles",titles)

#Begin Semantic Analysis


# Remove punctuation, then tokenize documents

punc = re.compile( '[%s]' % re.escape( string.punctuation ) )
term_vec = [ ]

for a in doc:
        a = a.lower()  #these aren't necessary if you're dealing with keywords
        a = punc.sub( '', a )
        term_vec.append( nltk.word_tokenize( a ) )

words = len(" ".join(doc))
# Print resulting term vectors
if alert == 0: 
    current_task.update_state(state='SCAN',
                meta={'current': 60, 'articles':0, 'words':words})
   
# Remove stop words from term vectors

stop_words = nltk.corpus.stopwords.words( 'english' )

for i in range( 0, len( term_vec ) ):
    term_list = [ ]

    for term in term_vec[ i ]:
        if term not in stop_words:
            term_list.append( term )

    term_vec[ i ] = term_list

if alert == 0: 
    current_task.update_state(state='SCAN',
                meta={'current':62, 'articles':0, 'words':words})
   
# Print term vectors with stop words removed
# stemming is difficult with the keyword extraction ....
    # Porter stem remaining terms

#porter = nltk.stem.porter.PorterStemmer()

#for i in range( 0, len( term_vec ) ):
#   for j in range( 0, len( term_vec[ i ] ) ):
#        term_vec[ i ][ j ] = porter.stem( term_vec[ i ][ j ] )

#  Convert term vectors into gensim dictionary

dict = gensim.corpora.Dictionary( term_vec )
new_dict = copy.deepcopy(dict)
#new_dict.filter_extremes(no_below=0, no_above=1, keep_n=vocsize)

 # old2new = {dict.token2id[token]:new_id for new_id, token in new_dict.iteritems()}
 # vt = gensim.modelsVocabTransform(old2new)

corp = [ ]
for i in range( 0, len( term_vec ) ):
    corp.append( new_dict.doc2bow( term_vec[ i ] ) )

#  Create TFIDF vectors based on term vectors bag-of-word corpora

# MmCorpus.serialize("{}.bow".format(prefix), vt[corp], progress_cnt=10000)
# corp = MmCorpus("{}.bow".format(prefix))


tfidf_model = gensim.models.TfidfModel( corp ,id2word=new_dict)

#  Create pairwise document similarity index
if alert == 0: 
    current_task.update_state(state='SCAN',
                meta={'current': 66, 'articles':0, 'words':words})
   
n = 20

corpus_tfidf= tfidf_model[corp]
lsi_model = gensim.models.LsiModel(corpus_tfidf, id2word=new_dict, num_topics=n) #
corpus_lsi = lsi_model[corpus_tfidf]
list_corpus = []
for dox in corpus_lsi:
    list_corpus.append(dox)
index = gensim.similarities.SparseMatrixSimilarity(corpus_lsi, num_features = n )

if alert == 0: 
    current_task.update_state(state='SCAN',
                meta={'current':75, 'articles':0, 'words':words})
   
#lda_model = gensim.models.LdaModel(corpus_tfidf, id2word=dict, num_topics=20) #initialize an LSI transformation
#index2 = gensim.similarities.SparseMatrixSimilarity(lda_model[corpus_tfidf], num_features = 50 )


#Begin Graph visualisation


thresh = 0.2-articlenumber/8000.#0.15#0.1/pow(upper/210,2)  #the higher the thresh, the less critical  
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

if alert == 0: 
    current_task.update_state(state='SCAN',
                meta={'current': 80, 'articles':0, 'words':words})
   
           
suggestions = Suggest.objects.filter(custom = 'last24h') 
suggestions.delete()
            
size= len(corp)
tg = nx.DiGraph()
tg.add_node(0,overall_size=size)


count_suggest = 1
count_comp = 1
big_list = []
small_list = []
keywords_in = ['ms','.','cookies','cookie','mr','_','-','2016']

graphs = sorted(nx.connected_component_subgraphs(ug),key=len,reverse=True)
graphx = sorted([[len(i), nx.average_clustering(i),i] for i in graphs],reverse=True)


for a in graphx:
    comp = a[2]
    if len(comp) >= 2:

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
        else: 
            timeinf = "no time information"
            time_disclaim = "no time information"

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

        #suggestion extraction
    # if len(comp) > 5:
    #   count_clique=1
    #   clique_count= 0
    #   closeness = nx.closeness_centrality(comp, distance=True)

    #   for k in sorted(list(nx.find_cliques(comp)),key = len, reverse=True):
    #       if len(k) >= 3:
    #           susvec = sorted([[closeness[r],r] for r in k], reverse=True)[0][1]
    #           if count_clique == 1:
    #               ug.node[susvec]['suggest'] = count_comp
    #               q = Suggest(custom= 'last24h', title = ug.node[susvec]['title'], url = ug.node[susvec]['url'], distance = count_comp, images = ug.node[susvec]['images'])
    #               q.save()
    #           else:
    #               small_list.append([len(comp)*len(k)/count_clique,susvec])
    #           #clique level keyword extraction
    #           all_words = []
    #           for j in k:
    #               for l in range(0,4):
    #                   x = sorted(list_corpus[j],key= lambda close:close[1],reverse=True)[l]
    #                   t = sorted([[float(i.split('*"')[0]),i.split('*"')[1].strip('" ')] for i in lsi_model.print_topics(n)[x[0]][1].split('+') if i.split('*"')[1].strip('" ') not in keywords_in],reverse=True)
    #                   s = [[a*x[1],b] for a,b in t] #weigh every word weight by topic weight
    #                   for item in s:
    #                       all_words.append(item)

    #           one_word = []
    #           for a in list(set([b for c,b in all_words if b not in keywords_in])):
    #               f = [[x,y] for x,y in all_words if y==a]
    #               one_word.append([sum([x for x,y in f]),a])
    #           a = sorted(one_word,reverse=True)
                

    #           if len(a) == 1:
    #               keywords = [a[0][1]]
    #               ug.node[susvec]['keywords'] = keywords
    #               #keywords_in.append(keywords[0])
    #           elif len(a) == 2:
    #               keywords = [a[0][1], a[1][1]]
    #               ug.node[susvec]['keywords'] = keywords
    #               #keywords_in.append(keywords[0])
    #               #keywords_in.append(keywords[1])
                    
    #           else:
    #               keywords = ''

    #           tg.add_node(count_comp*100+count_clique-1, size=len(k),name=keywords)
    #           tg.add_edge(count_comp,count_comp*100+count_clique-1)

    #           clique_count += len(k)
    #           count_clique += 1
    #   tg.add_node(count_comp*100+count_clique-1, size=len(comp)-clique_count)
    #   tg.add_edge(count_comp,count_comp*100+count_clique-1)   #this last node is the one corresponding to all nodes that are not in any clique, i.e. it is on the level of cliques, not comps
    #   count_comp += 1

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

if alert == 0: 
    current_task.update_state(state='VISUALISE',
                meta={'current': 90, 'articles':0, 'words':words})
   

# tg.add_edge(0,50)
# tg.add_node(5000, size= 0)
# tg.add_edge(50,5000)  
tg.node[0]['final_size']=len(ug.nodes())
tg.node[0]['comps'] = count_comp-1
ug.graph['size']=len(ug.nodes())
ug.graph['comps'] = count_comp-1


#at first there should be an article for every survining comp, then we fill up via biglist. 

#suggestions for database
# maxcount = 15
# count_suggest = count_comp-1
# for m in sorted(small_list,reverse=True):
#     if count_suggest <= maxcount:
#         if ((False not in [ug.node[k]['suggest'] == 0 for k in ug.neighbors(m[1])]) and (ug.node[m[1]]['suggest'] == 0))and (len(list_corpus[m[1]]) > 1):
#             ug.node[susvec]['suggest'] = count_suggest
#             q = Suggest(custom= 'last24h', title = ug.node[m[1]]['title'], url = ug.node[m[1]]['url'], distance = count_suggest, images = ug.node[m[1]]['images'])
#             q.save()
#             count_suggest += 1                                      


#export
from networkx.readwrite import json_graph
ug_nl = json_graph.node_link_data(ug)
tgt = json_graph.tree_data(tg,root=0)
with open(settings.STATIC_BREV + static('last24h/cs/cs_'+ strin +'_tgt_cluster.json'), 'w+') as fp:
    json.dump(tgt,fp)
with open(settings.STATIC_BREV + static('last24h/cs/cs_'+ strin +'_nl.json'), 'w+') as fp:
    json.dump(ug_nl,fp)


q = Query.objects.filter(string= strin)
for query in q:
    query.articlenumber = articlenumber
    query.words = words
    query.save()

if alert == 0:
    current_task.update_state(state='SUCCESS',
                meta={'current': 99, 'articles':0, 'words':len(doc)})



#send_mail('successful update', 'Successful update. headlines are:' , 'grphtcontact@gmail.com', ['pvboes@gmail.com'])