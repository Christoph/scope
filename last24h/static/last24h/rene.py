global exitFlag, workQueue, queueLock, articlenumber

print strin
import email, imaplib, os,sys
import urllib2
from datetime import date, timedelta
from urlparse import urlparse

reload(sys)
sys.setdefaultencoding('utf8')



detach_dir = '.' # directory where to save attachments (default: current)
user = "renesnewsletter"
pwd = "renewilllesen"
# connecting to the gmail imap server
m = imaplib.IMAP4_SSL("imap.gmail.com")
m.login(user,pwd)
m.select("[Gmail]/All Mail") # here you a can choose a mail box like INBOX instead

# use m.list() to get all the mailboxes

yesterday = date.today() - timedelta(hours=24)

resp, items = m.search(None, '(SINCE "'+ yesterday.strftime("%d-%b-%Y")+'")') # you could filter using the IMAP rules here (check http://www.example-code.com/csharp/imap-search-critera.asp)
#at this step we want to download all the relevant mails since the last newsletter. There should be filters for this.
items = items[0].split() # getting the mails id
print items

subscribed_urls = ["launch.us","launch.co","index.co","azhar","getrevue.co","morningreader.com","producthunt.com","betalist","crunchable","mailchimp.com","facebook.com","twitter.com","launchticker","play.google.com","www.technologyreview.com/newsletters","launchevents.typeform.com","ev.inside.com","itunes.apple.com","https://www.technologyreview.com/?utm_source","typeform","producthunt.us3.list-manage.com","getfeedback","youtube.com","forms/"]
all_urls = [] 
no_urls = 0
#senders = ''
senders_list = []
#for emailid in range(int(items[2]),int(items[2])+2):
for emailid in items:
    resp, data = m.fetch(emailid, "(RFC822)") # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
    email_body = data[0][1] # getting the mail content
    urls = list(set([i.split('"')[0].replace("=","").replace("3D","=") for i in email_body.replace("\r\n","").split('href=3D"') if i[0:4] == 'http']))#[i.split('"')[0].replace("=","").replace("click?upn3D","click?upn=") for i in email_body.replace("\r\n","").split('href=3D"') if i[0:4] == 'http']
    no_urls = no_urls + len(urls)
    mail = email.message_from_string(email_body) # parsing the mail content to get a mail object
    sender, encoding = email.Header.decode_header(email.utils.parseaddr(mail.get('from'))[0])[0]
    senders_list.append(sender)
    senders = '<br/>'.join(list(set(senders_list)))#senders + sender + '<br/>'
    for url in urls:
        try:
            req = urllib2.Request(url)
            res = urllib2.urlopen(req)
            finalurl = res.geturl()
            check_url = urlparse(finalurl)
            print finalurl
        except:
            continue
        # somehow just using all(x not in finalurl for x in subscribed_urls) the django shell doesn't manage
        test_list = []
        for x in subscribed_urls:
            if x in finalurl:
                test_list.append("yes")
        if len(test_list) == 0 and (check_url.path != '/' and check_url.path != '' and check_url.path != '/en/') :
            all_urls.append(finalurl)


#urlss = open('urls.txt','w+')
#urlss.write("AND".join(all_urls))
#urlss.close()



    # #Check if any attachments at all
    # if mail.get_content_maintype() != 'multipart':
    #     continue

    # print "["+mail["From"]+"] :" + mail["Subject"]

    # # we use walk to create a generator so we can iterate on the parts and forget about the recursive headach
    # for part in mail.walk():
    #     # multipart are just containers, so we skip them
    #     if part.get_content_maintype() == 'multipart':
    #         continue

    #     # is this part an attachment ?
    #     if part.get('Content-Disposition') is None:
    #         continue

    #     filename = part.get_filename()
    #     counter = 1

    #     # if there is no filename, we create one with a counter to avoid duplicates
    #     if not filename:
    #         filename = 'part-%03d%s' % (counter, 'bin')
    #         counter += 1

    #     att_path = os.path.join(detach_dir, filename)

    #     #Check if its already there
    #     if not os.path.isfile(att_path) :
    #         # finally write the stuff
    #         fp = open(att_path, 'wb')
    #         fp.write(part.get_payload(decode=True))
    #         fp.close()








# def return_articles(feeds):
#     articles_info = []
#     for feed in feeds:
#         d = feedparser.parse(feed)
#         for i in range(0, len(d.entries)-1):
#             dd = Article(d.entries[i].link, language='en')#, fetch_images = False)#link.split('url=')[1]
#             if hasattr(d.entries[i],'summary'):
#                 aa = d.entries[i].summary
#                 if "<div>" in aa:
#                     aa = aa.split("<div>")[0] + " " + aa.split("<div>")[2]

#             else:
#                 aa = ''
#             if hasattr(d.entries[i],'published_parsed'):
#                 ff = datetime.fromtimestamp(mktime(d.entries[i].published_parsed))
#             else:
#                 ff = None
#             articles_info.append([dd,aa,ff])#,ff    
#     return articles_info
    
# Determine scources and mode of extraction
            
#Via Googlefeed

#feeds = ['http://feeds.guardian.co.uk/theguardian/world/rss','http://www.themoscowtimes.com/rss/top/','http://www.spiegel.de/international/index.rss','http://mondediplo.com/backend','http://feeds.bbci.co.uk/news/business/rss.xml','http://www.independent.co.uk/news/world/rss','http://www.nytimes.com/services/xml/rss/nyt/InternationalHome.xml','http://www.aljazeera.com/xml/rss/all.xml','feed://timesofindia.feedsportal.com/c/33039/f/533916/index.rss','http://feeds.washingtonpost.com/rss/world/asia-pacific','http://www.telegraph.co.uk/finance/economics/rss','feed://www.thejc.com/feed/news','http://feeds.bbci.co.uk/news/technology/rss.xml','feed://www.buenosairesherald.com/articles/rss.aspx','feed://muslimnews.co.uk/feed/?post_type=news','http://www.latimes.com/world/rss2.0.xml','http://feeds.chicagotribune.com/chicagotribune/news','http://feeds.feedburner.com/TheAustralianTheWorld']
 
#non_keywords = set(('World news','Europe','Africa','USA','Technology','Approved','Password','Biography'))
#articles_info = return_articles(all_urls)

articles = [Article(x) for x in list(set(all_urls))]
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

# class myThread (threading.Thread):
#    def __init__(self, threadID, name, q):
#      threading.Thread.__init__(self)
#      self.threadID = threadID
#      self.name = name
#      self.q = q
#    def run(self):
#      #print "Starting " + self.name
#      process_data(self.name, self.q)
#      #print "Exiting " + self.name

# def process_data(threadName, q):
#    while not exitFlag:
#       queueLock.acquire()
#       if not workQueue.empty():
#           data = q.get()
#       queueLock.release()
#       data.download()
#       data.parse()
#         #print " %s processing" % (threadName)
#   else:
#       queueLock.release()
#   time.sleep(1)

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
exclude = set(('', 'FT.com / Registration / Sign-up','Error','404 Page not found','Page no longer available', 'File or directory not found','Page not found','Content not found'))

unsubscribe_exclude = "If you are not redirected automatically, please click the Unsubscribe button below"

counter = 0
words = 0
for i in range(0,upper-1):
    article = articles[i]
    words += len(" ".join(article.text))
    if article.title not in exclude and unsubscribe_exclude not in article.text and "tech" in article.text:
        doc.append(article.text)
        titles.append(article.title)
        urls.append(article.url)
        images.append(article.top_image)
        #times.append(articles_info[i][2])
        summary.append(article.text[0:400] + "...")
        try:
            print article.text
        except:
            pass
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

n = 40

corpus_tfidf= tfidf_model[corp]

lsi_model = gensim.models.LsiModel(corpus_tfidf, id2word=dict, num_topics=n) #
corpus_lsi = lsi_model[corpus_tfidf]
list_corpus = []
for dox in corpus_lsi:
    list_corpus.append(dox)
index = gensim.similarities.SparseMatrixSimilarity(corpus_lsi, num_features = n )

#lda_model = gensim.models.LdaModel(corpus_tfidf, id2word=dict, num_topics=20) #initialize an LSI transformation
#index2 = gensim.similarities.SparseMatrixSimilarity(lda_model[corpus_tfidf], num_features = 50 )

gensim.corpora.MmCorpus.serialize(settings.STATIC_ROOT + 'last24h/rene_data/rene.mm',corp)#/home/django/graphite/static/last24h/l24h.mm', corp)
dict.save(settings.STATIC_ROOT + 'last24h/rene_data/rene.dict')
lsi_model.save(settings.STATIC_ROOT + 'last24h/rene_data/rene.lsi')
index.save(settings.STATIC_ROOT + 'last24h/rene_data/rene.index')
#lda_model.save('/tmp/model.lda') 


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
    ug.add_node(i,title=titles[i],url=urls[i],suggest=0, summary = summary[i],images = images[i], comp = 0,source= source,keywords='',time=None)#, time = times[i])#,keywords=keywords[i])

graphs = []
score_new = 0
score_old = -1
best_thresh = 0.
best_score = 0
#thresh = 0.02

#Now trying two steps: In the first, get the bigguest cluster (which should correspond to tech topics) and then in a second step maximise the number of clusters in it

orignumber = len(ug)
print str(len(ug)) + " old graph"

for s in [x/1000. for x in xrange(0,500)]:


#while score_new >= score_old:#len(graphs) not in [5,6] and any(len(x) <4 for x in graphs):
    ug.remove_edges_from(ug.edges())

    for i in range( 0, len( corpus_tfidf ) ): 
        sim = index[ lsi_model[ corp [ i ] ] ]
        for j in range( i+1, len( sim ) ):
            dist = (1. - sim[j])/2.
            if dist < s:
                ug.add_edge(i,j,{'weight':dist})
    graphs = sorted(nx.connected_component_subgraphs(ug),key=len,reverse=True)

    test = [x for x in graphs if len(x) >= 4]#20>= 
    test2 = [len(x) for x in test]
    if len(test2) != 0:
        score_new = sum(test2) #test2[0]
    #score_new = [len(test),sum(test2)]
    
    if score_new > best_score and len(test) == 5:
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



#thresh -= 0.002
print best_thresh
ug.remove_edges_from(ug.edges())
for i in range( 0, len( corpus_tfidf ) ): 
    sim = index[ lsi_model[ corp [ i ] ] ]
    for j in range( i+1, len( sim ) ):
        dist = (1. - sim[j])/2.
        if dist < best_thresh:
            ug.add_edge(i,j,{'weight':dist})
graphs = sorted(nx.connected_component_subgraphs(ug),key=len,reverse=True)



# for i in range(2,len(graphs)):
#     ug.remove_nodes_from(graphs[i])

#tech_ratio = orignumber/float(len(ug))

# print str(len(ug)) + " new graph"
# print "Second Round"

# best_thresh = 0.
# best_score = 0#[0,0]

# for s in [x/1000. for x in xrange(0,500)]:


# #while score_new >= score_old:#len(graphs) not in [5,6] and any(len(x) <4 for x in graphs):
#     ug.remove_edges_from(ug.edges())

#     for i in range(0,len( corpus_tfidf )): 
#         sim = index[ lsi_model[ corp [ i ] ] ]
#         for j in range( i+1, len( sim ) ):
#             dist = (1. - sim[j])/2.
#             if dist < s and j in ug and i in ug:
#                 ug.add_edge(i,j,{'weight':dist})
#     graphs = sorted(nx.connected_component_subgraphs(ug),key=len,reverse=True)

#     test = [x for x in graphs if 20>= len(x) >= 3]
#     test2 = [len(x) for x in test]
#     #score_new = test2[0]
#     score_new = sum(test2) #[len(test),sum(test2)]
    
#     if score_new > best_score and 15>= len(test) >= 3:
#         best_score = score_new
#         best_thresh = s

#     #print thresh
#     #thresh += 0.001
#     print s
#     print len(graphs)
#     # for i in graphs:
#     #     for ii in i:
#     #         print ug.node[ii]['title']
#     #     print "and"
#     #print test2
#     print score_new
#     print best_thresh
#     # if thresh >= 0.5:
#     #     break

 
dispersion = str(int(float(1-2*best_thresh)*100)) + '%'
# print best_thresh
# ug.remove_edges_from(ug.edges())
# for i in range( 0, len( corpus_tfidf ) ): 
#     sim = index[ lsi_model[ corp [ i ] ] ]
#     for j in range( i+1, len( sim ) ):
#         dist = (1. - sim[j])/2.
#         if dist < best_thresh and j in ug and i in ug:
#             ug.add_edge(i,j,{'weight':dist})
# graphs = sorted(nx.connected_component_subgraphs(ug),key=len,reverse=True)

# print graphs


# suggestions = Suggest.objects.filter(custom = 'last24h') 
# suggestions.delete()
            
size= len(corp)
tg = nx.DiGraph()
tg.add_node(0,overall_size=size)

# tg2 = nx.DiGraph()
# tg2.add_node(0,overall_size=size)


#n = 100
count_suggest = 1
count_comp = 1
big_list = []
small_list = []
keywords_in = ['ms','.','cookies','cookie','mr','_','-','2016']


graphx = sorted([[len(i), nx.average_clustering(i),i] for i in graphs],reverse=True)

#strin = "rene" + date.today().isoformat()

for a in graphx:
    comp = a[2]
    if len(comp) >= 3:
        # first take care of the time signatures of the articles for the detail view
        # timespartition = sorted(list(set([ug.node[i]['time'] for i in comp.nodes() if ug.node[i]['time'] != None]))) #collect the different times occuring 
        # if len(timespartition) != 0:
        #     first_time = timespartition[0]
        #     last_time = timespartition[-1]
        #     onlytimes = []
        #     for a in timespartition:
        #        onlytimes.append([i for i in comp.nodes() if ug.node[i]['time'] == a]) # partition the set of times into articles with the same timestamp
        #     if first_time != last_time: #in case they're all published at the same time
        #         time_span = (last_time - first_time).total_seconds()
        #     else:
        #         time_span = 1
        #     #calculate positions on circle, reserving at least 355-5 deg for ones without timestamp.
        #     notime = [ug.node[i]['time'] for i in comp.nodes() if ug.node[i]['time'] == None]
        #     ratio = len(notime)/len(comp)
        #     notime_count = 1
        #     #take care of positioning of articles with the same timestamp
        #     for a in onlytimes:
        #         relcount = 0
        #         for i in a:
        #             if len(a) > 1:
        #                 ug.node[i]['time_pos'] = (last_time - ug.node[i]['time']).total_seconds()/time_span*350*(1-ratio) + 5 + ratio*175 + relcount/(len(a)-1)*5-5*len(a)/2
        #                 relcount += 1
        #             else:  
        #                 ug.node[i]['time_pos'] = (last_time - ug.node[i]['time']).total_seconds()/time_span*350*(1-ratio) + 5 + ratio*175
        #             #translate into isoformat for display
        #             ug.node[i]['time'] = ug.node[i]['time'].isoformat()


        #     #display formatting of time
        #     if len(notime) == len(comp): #none of the nodes has a timestamp
        #         time_disclaim = 'no timestamp for this cluster'
        #         timeinf = ['','','','','']
        #     elif time_span == 1: #all of those nodes that have a timestamp have the same one
        #         time_disclaim = 'no timestamp'
        #         timeinf = ['','',ug.node[i]['time'],'','']
        #     else: 
        #         now = datetime.now().isoformat()
        #         now = now[5:7] + '/' + now[8:10] + ' ' + now[11:13] + 'h <br>(GMT)'
        #         time_disclaim = 'no timestamp'
        #         t_hours = time_span/3600
        #         if int(t_hours/4/24) == 0:
        #             tt1 = str(int(t_hours/4%24)) + 'h'
        #         elif int(t_hours/4%24) == 0:
        #             tt1 = str(int(t_hours/4/24)) + 'd '
        #         else:
        #             tt1 = str(int(t_hours/4/24)) + 'd ' + str(int(t_hours/4%24)) + 'h'
        #         if int(t_hours/2/24) == 0:
        #             tt2 = str(int(t_hours/2%24)) + 'h'
        #         elif int(t_hours/2%24) == 0:
        #             tt2 = str(int(t_hours/2/24)) + 'd '
        #         else:
        #             tt2 = str(int(t_hours/2/24)) + 'd ' + str(int(t_hours/2%24)) + 'h'
        #         if int(3*t_hours/4/24) == 0:
        #             tt3 = str(int(3*t_hours/4%24)) + 'h'
        #         elif int(3*t_hours/4%24) == 0:
        #             tt3 = str(int(3*t_hours/4/24)) + 'd '
        #         else:
        #             tt3 = str(int(3*t_hours/4/24)) + 'd ' + str(int(3*t_hours/4%24)) + 'h'
        #         if int(t_hours/24) == 0:
        #             tt4 = str(int(t_hours%24)) + 'h'
        #         elif int(t_hours/4%24) == 0:
        #             tt4 = str(int(t_hours/4/24)) + 'd '
        #         else:
        #             tt4 = str(int(t_hours/24)) + 'd ' + str(int(t_hours%24)) + 'h'
        #         timeinf = [now,tt1,tt2,tt3,tt4]
        # else: 
        #     timeinf = "no time information"
        #     time_disclaim = "no time information"

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


        #keywords = [a[0][1], a[1][1]]
        # else:
        #   for i in comp:
        #       ug.node[i]['comp'] = count_comp
        #       ug.node[i]['single'] = 0
        #   all_words = []
        #   # compile a list of all words, directly with the weightings. Then merge this big list.
        #   for j in range(0,2):
        #       x = sorted(list_corpus[i],key= lambda close:close[1],reverse=True)[j]
        #       t = sorted([[float(z.split('*"')[0]),z.split('*"')[1].strip('" ')] for z in lsi_model.print_topics(n)[x[0]][1].split('+') if z.split('*"')[1].strip('" ') not in keywords_in],reverse=True)
        #       s = [[a*x[1],b] for a,b in t] #weigh every word weight by topic weight
        #       for item in s:
        #           all_words.append(item)  

        
        #   one_word = []
        #   for a in list(set([b for c,b in all_words if b not in keywords_in])):
        #       f = [[x,y] for x,y in all_words if y==a]
        #       one_word.append([sum([x for x,y in f]),a])
        #   a = sorted(one_word,reverse=True)

        #   if len(a) != 0:
        #       keywords = a[0][1] + ", " + a[1][1]
        #       #keywords_in.append(keywords[0])
        #       #keywords_in.append(keywords[1])
        #   else: keywords = ''

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
        q = Suggest(custom= strin, title = ug.node[susvec]['title'], url = ug.node[susvec]['url'], distance = count_comp, images = ug.node[susvec]['images'], keywords = keywords,source=ug.node[susvec]['source'])
        q.save()

                #add the nodes for the arc
        tg.add_node(count_comp, clustering=clustering,name=keywords)  
        tg.add_edge(0,count_comp) 

        # if cnode['time'] != None:
        #     mobile_cluster_desc = '<strong>' + str(keywords) + '</strong><br/><p># of articles: '+ str(len(comp))+ '<p>Clustering: ' + str(clustering) + '%</br><a href=' + cnode['url'] + '>' + cnode['title'] + '</a><br/><br/>' + cnode['source']  + '   ' + cnode['time'][5:7] + '/' + cnode['time'][8:10] + ' ' + cnode['time'][11:16] + '<br/><br/>'
        # else: 
        #     mobile_cluster_desc = '<strong>' + str(keywords) + '</strong><br/><p># of articles: '+ str(len(comp))+ '<p>Clustering: ' + str(clustering) + '%</br><a href=' + cnode['url'] + '>' + cnode['title'] + '</a><br/><br/>' + cnode['source'] 
        # tg2.add_node(count_comp, clustering=clustering,name=mobile_cluster_desc)  
        # tg2.add_edge(0,count_comp)

        # for i in range (0,len(ordering)-1):
        #     cnode = ug.node[ordering[i][0]]
        #     if cnode['time'] != None:
        #         tg2.add_node(count_comp*100+i, size=len(comp),name= '<a href=' + cnode['url']  + '>' + cnode['title'] + '</a><br/><br/>' + cnode['source']  + '   ' + cnode['time'][5:7] + '/' + cnode['time'][8:10] + ' ' + cnode['time'][11:16] + '<br/><br/>')
        #     else:
        #         tg2.add_node(count_comp*100+i, size=len(comp),name= '<a href=' + cnode['url']  + '>' + cnode['title'] + '</a><br/><br/>' + cnode['source'])
        #     tg2.add_edge(count_comp,count_comp*100+i)
        #     if cnode['time'] != None:
        #         tg2.add_node(count_comp*1000+i, size=len(comp),name= '<a href=' + cnode['url']  + '>' + cnode['title'] + '</a><br/><br/>' + cnode['source']  + '   ' + cnode['time'][5:7] + '/' + cnode['time'][8:10] + ' ' + cnode['time'][11:16] + '<br/><br/>' + cnode['summary'])
        #     else: 
        #         tg2.add_node(count_comp*100+i, size=len(comp),name= '<a href=' + cnode['url']  + '>' + cnode['title'] + '</a><br/><br/>' + cnode['source']  + '   ' + cnode['summary'])
        #     tg2.add_edge(count_comp*100+i,count_comp*1000+i)

           

        tg.add_node(count_comp*100, size=len(comp))
        tg.add_edge(count_comp,count_comp*100)
        count_comp += 1
    else:

        ug.remove_nodes_from(comp)



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
ug.graph['senders'] = senders
ug.graph['thresh'] = best_thresh
ug.graph['dispersion'] = dispersion
ug.graph['tech-nontech-ratio'] = str(len(doc)/float(articlenumber))#str(tech_ratio)
ug.graph['wordcount'] = str(words)
ug.graph['links'] = str(no_urls)
ug.graph['articlenumber'] = str(articlenumber)

#export
from networkx.readwrite import json_graph
ug_nl = json_graph.node_link_data(ug)
tgt = json_graph.tree_data(tg,root=0)
#tgt_mobile = json_graph.tree_data(tg2,root=0)
with open(settings.STATIC_ROOT + 'last24h/cs/cs_'+ strin +'_tgt_cluster.json', 'w+') as fp:
    json.dump(tgt,fp)
# with open(settings.STATIC_ROOT + 'last24h/cs/cs_'+ strin +'_tgt_mobile.json', 'w+') as fp:
#     json.dump(tgt_mobile,fp)
with open(settings.STATIC_ROOT + 'last24h/cs/cs_'+ strin +'_nl.json', 'w+') as fp:
    json.dump(ug_nl,fp)


q = Query.objects.filter(string= strin)
for query in q:
    query.articlenumber = articlenumber
    query.words = words
    query.save()
#send_mail('successful update', 'Successful update. headlines are:' , 'grphtcontact@gmail.com', ['pvboes@gmail.com'])
