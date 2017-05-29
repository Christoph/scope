import email
import imaplib
import sys
import urllib.request, urllib.error, urllib.parse
from datetime import date, timedelta
from urllib.parse import urlparse
from networkx.readwrite import json_graph

global exitFlag, workQueue, queueLock, articlenumber

print(strin)

reload(sys)
sys.setdefaultencoding('utf8')


detach_dir = '.'  # directory where to save attachments (default: current)
# user="enews@neulandherzer.net"
# pwd = "Ensemble_Enema"
# m = imaplib.IMAP4_SSL("imap.1und1.de")
# m.login(user,pwd)
# m.select("INBOX")


user = "renesnewsletter"
pwd = "renewilllesen"
# connecting to the gmail imap server
m = imaplib.IMAP4_SSL("imap.gmail.com")
m.login(user, pwd)
# here you a can choose a mail box like INBOX instead
m.select("[Gmail]/All Mail")

# use m.list() to get all the mailboxes

yesterday = date.today() - timedelta(hours=24)

# you could filter using the IMAP rules here (check
# http://www.example-code.com/csharp/imap-search-critera.asp)
resp, items = m.search(
    None, '(SINCE "' + yesterday.strftime("%d-%b-%Y") + '")')
# at this step we want to download all the relevant mails since the last
# newsletter. There should be filters for this.
items = items[0].split()  # getting the mails id
print(items)

subscribed_urls = ["launch.us", "launch.co", "index.co", "azhar", "getrevue.co","morningreader.com", "producthunt.com", "betalist", "crunchable", "mailchimp.com", "facebook.com", "twitter.com", "launchticker", "play.google.com", "www.technologyreview.com/newsletters",
                   "launchevents.typeform.com", "ev.inside.com", "itunes.apple.com", "https://www.technologyreview.com/?utm_source", "typeform", "producthunt.us3.list-manage.com", "getfeedback", "youtube.com", "forms/", "smashingmagazine", "wikipedia.org"]
all_urls = []
no_urls = 0
senders_list = []
# for emailid in range(int(items[2]),int(items[2])+2):
for emailid in items:
    # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can
    # ask for headers only, etc
    resp, data = m.fetch(emailid, "(RFC822)")
    email_body = data[0][1]  # getting the mail content
    # [i.split('"')[0].replace("=","").replace("click?upn3D","click?upn=") for i in email_body.replace("\r\n","").split('href=3D"') if i[0:4] == 'http']
    urls = list(set([i.split('"')[0].replace("=", "").replace("3D", "=")
                     for i in email_body.replace("\r\n", "").split('href=3D"') if i[0:4] == 'http']))
    no_urls = no_urls + len(urls)
    # parsing the mail content to get a mail object
    mail = email.message_from_string(email_body)
    sender, encoding = email.Header.decode_header(
        email.utils.parseaddr(mail.get('from'))[0])[0]
    senders_list.append(sender)
    # senders + sender + '<br/>'
    senders = '<br/>'.join(list(set(senders_list)))
    for url in urls:
        try:
            req = urllib.request.Request(url)
            res = urllib.request.urlopen(req)
            finalurl = res.geturl()
            check_url = urlparse(finalurl)
            print(finalurl)
        except:
            continue
        # somehow just using all(x not in finalurl for x in subscribed_urls)
        # the django shell doesn't manage
        test_list = []
        for x in subscribed_urls:
            if x in finalurl:
                test_list.append("yes")
        if len(test_list) == 0 and (check_url.path != '/' and check_url.path != '' and check_url.path != '/en/'):
            all_urls.append(finalurl)

articles = [Article(x) for x in list(set(all_urls))]
if len(articles) != 0:
    articlenumber = len(articles)
else:
    articlenumber = 1
upper = min(600, len(articles))

# for a in articles:
#     a.download()

# print "Start threading"

# #Threading stuff

exitFlag = 0

maxthread = 200
if upper < maxthread:
    threadlimit = upper
else:
    threadlimit = maxthread

threadList = []
for i in range(1, threadlimit):
    threadList.append(str(i))

nameList = articles[1:upper]
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
print("Exiting Main Thread")

# Putting together

doc = []
keywords = []
summary = []
titles = []
urls = []
times = []
images = []
exclude = set(('', 'FT.com / Registration / Sign-up', 'Error', '404 Page not found',
               'Page no longer available', 'File or directory not found', 'Page not found', 'Content not found'))

unsubscribe_exclude = "If you are not redirected automatically, please click the Unsubscribe button below"

counter = 0
words = 0
for i in range(0, upper - 1):
    article = articles[i]
    words += len(" ".join(article.text))
    # and "tech" in article.text:
    if article.title not in exclude and unsubscribe_exclude not in article.text:
        doc.append(article.text)
        titles.append(article.title)
        urls.append(article.url)
        images.append(article.top_image)
        # times.append(articles_info[i][2])
        summary.append(article.text[0:400] + "...")
        # try:
        #     print article.text
        # except:
        #     pass
        # keywords.append(articles_info[i][2])

#        keywords.append(article.keywords)

# Begin Semantic Analysis

# Remove punctuation, then tokenize documents


punc = re.compile('[%s]' % re.escape(string.punctuation))
term_vec = []

for a in doc:
    a = a.lower()  # these aren't necessary if you're dealing with keywords
    a = punc.sub('', a)
    term_vec.append(nltk.word_tokenize(a))


# Print resulting term vectors

# Remove stop words from term vectors

stop_words = nltk.corpus.stopwords.words('english')

for i in range(0, len(term_vec)):
    term_list = []

    for term in term_vec[i]:
        if term not in stop_words:
            term_list.append(term)

    term_vec[i] = term_list

# Print term vectors with stop words removed
# stemming is difficult with the keyword extraction ....
    # Porter stem remaining terms

porter = nltk.stem.porter.PorterStemmer()

for i in range(0, len(term_vec)):
    for j in range(0, len(term_vec[i])):
        term_vec[i][j] = porter.stem(term_vec[i][j])

#  Convert term vectors into gensim dictionary

dict = gensim.corpora.Dictionary(term_vec)
corp = []
for i in range(0, len(term_vec)):
    corp.append(dict.doc2bow(term_vec[i]))

#  Create TFIDF vectors based on term vectors bag-of-word corpora

tfidf_model = gensim.models.TfidfModel(corp)

#  Create pairwise document similarity index


corpus_tfidf = tfidf_model[corp]
# lsi_model = gensim.models.LsiModel(corpus_tfidf, id2word=dict, num_topics=n1) #
# corpus_lsi = lsi_model[corpus_tfidf]
# list_corpus = []
# # for dox in corpus_lsi:
# #     list_corpus.append(dox)
# index = gensim.similarities.SparseMatrixSimilarity(corpus_lsi, num_features = n1 )

# lda_model = gensim.models.LdaModel(corpus_tfidf, id2word=dict, num_topics=20) #initialize an LSI transformation
#index2 = gensim.similarities.SparseMatrixSimilarity(lda_model[corpus_tfidf], num_features = 50 )

# /home/django/graphite/static/last24h/l24h.mm', corp)
gensim.corpora.MmCorpus.serialize(
    settings.STATIC_ROOT + 'rene/rene_data/rene.mm', corp)
dict.save(settings.STATIC_ROOT + 'rene/rene_data/rene.dict')
# lsi_model.save(settings.STATIC_ROOT + 'rene/rene_data/rene.lsi')
# index.save(settings.STATIC_ROOT + 'rene/rene_data/rene.index')
# lda_model.save('/tmp/model.lda')


# Begin Graph visualisation

# 3-articlenumber*0.03/500#0.1/pow(upper/210,2)  #the higher the thresh,
# the more critical
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
    ug.add_node(i, title=titles[i], url=urls[i], suggest=0, summary=summary[i], images=images[
                i], comp=0, source=source, keywords='', time=None)  # , time = times[i])#,keywords=keywords[i])

ug_nl = json_graph.node_link_data(ug)
#tgt_mobile = json_graph.tree_data(tg2,root=0)
with open(settings.STATIC_ROOT + 'last24h/rene_all.json', 'w+') as fp:
    json.dump(ug_nl, fp)


graphs = []
score_new = 0
best_thresh = 0.
best_score = 0
#thresh = 0.02

# Now trying two steps: In the first, get the bigguest cluster (which
# should correspond to tech topics) and then in a second step maximise the
# number of clusters in it

orignumber = len(ug)
print("First Round")
print(str(len(ug)) + " old graph")

# for s in [x/1000. for x in xrange(0,500)]:


# #while score_new >= score_old:#len(graphs) not in [5,6] and any(len(x) <4 for x in graphs):
#     ug.remove_edges_from(ug.edges())

#     for i in range( 0, len( corpus_tfidf ) ):
#         sim = index[ lsi_model[ corp [ i ] ] ]
#         for j in range( i+1, len( sim ) ):
#             dist = (1. - sim[j])/2.
#             if dist < s:
#                 ug.add_edge(i,j,{'weight':dist})
#     graphs = sorted(nx.connected_component_subgraphs(ug),key=len,reverse=True)

#     test = [x for x in graphs if len(x) >= 3]#20>=
#     exclude = [x.nodes() for x in graphs if x not in test]
#     test2 = [len(x) for x in test]
#     if len(test) == 2:
#         score_new = len(test[0])*len(test[1])#reduce(mul, test2,1)#len(test[0])+len(test[1])
#     #score_new = [len(test),sum(test2)]
#     elif len(test) >= 3:
#         score_new = len(test[0])*len(test[1])*len(test[2])

#     if score_new > best_score and len(test) >= 3:
#         best_score = score_new
#         best_thresh = s

# print thresh
#thresh += 0.001
# print s
# print len(graphs)
# # for i in graphs:
# #     for ii in i:
# #         print ug.node[ii]['title']
# #     print "and"
# #print test2
# print score_new
# print best_thresh
# if thresh >= 0.5:
#     break


#thresh -= 0.002
# print best_thresh
# ug.remove_edges_from(ug.edges())
# for i in range( 0, len( corpus_tfidf ) ):
#     sim = index[ lsi_model[ corp [ i ] ] ]
#     for j in range( i+1, len( sim ) ):
#         dist = (1. - sim[j])/2.
#         if dist < best_thresh:
#             ug.add_edge(i,j,{'weight':dist})
# graphs = sorted(nx.connected_component_subgraphs(ug),key=len,reverse=True)
# test = [x for x in graphs if len(x) >= 3]#20>=
# exclude = [x.nodes() for x in graphs if x not in test]
# for graph in graphs:
#     print graph
#     for no in graph:
#         print ug.node[no]['title']


# for graph in test:
#     print "\n CLUSTER: \n"
#     for no in graph:
#         try:
#             print ug.node[no]['title'], ug.node[no]['source'], no
#         except:
#             pass
# print "\n AND \n"
# for no in list(set().union(*exclude)):
#     try:
#         print ug.node[no]['title'], ug.node[no]['source'], no
#     except:
#         pass

# print "\n SECOND ROUND \n"

# for i in range(1,len(graphs)):
#     ug.remove_nodes_from(graphs[i].nodes())

# print str(len(ug)) + " new graph"

lsi_model2 = gensim.models.LsiModel(corpus_tfidf, id2word=dict, num_topics=n2)
corpus_lsi2 = lsi_model2[corpus_tfidf]
# list_corpus = []
# for dox in corpus_lsi:
#     list_corpus.append(dox)
index2 = gensim.similarities.SparseMatrixSimilarity(
    corpus_lsi2, num_features=n2)

lsi_model2.save(settings.STATIC_ROOT + 'rene/rene_data/l24h2.lsi')
index2.save(settings.STATIC_ROOT + 'rene/rene_data/l24h2.index')

best_thresh = 0.
best_score = 0  # [0,0]

for s in [x / 1000. for x in range(0, 500)]:

    # while score_new >= score_old:#len(graphs) not in [5,6] and any(len(x) <4
    # for x in graphs):
    ug.remove_edges_from(ug.edges())

    for i in range(0, len(corpus_tfidf)):
        sim = index2[lsi_model2[corp[i]]]
        for j in range(i + 1, len(sim)):
            dist = (1. - sim[j]) / 2.
            if dist < s and j in ug and i in ug:
                ug.add_edge(i, j, {'weight': dist})
    graphs = sorted(nx.connected_component_subgraphs(ug),
                    key=len, reverse=True)

    test = [x for x in graphs if 20 > len(x) >= 3]
    exclude = [x.nodes() for x in graphs if x not in test]
    #test2 = [len(x) for x in test]
    if len(test) >= 2:
        # len(test[0])+len(test[1])#sum(test2)#len(test)#test2[0]
        score_new = len(test)
        #score_new = [len(test),sum(test2)]

    # score_new = sum(test2) #[len(test),sum(test2)]

    if score_new > best_score and len(test) >= 3:
        best_score = score_new
        best_thresh = s

        # print thresh
        #thresh += 0.001
        print(s)
        print(len(graphs))
        # for i in graphs:
        #     for ii in i:
        #         print ug.node[ii]['title']
        #     print "and"
        # print test2
        print(score_new)
        print(best_thresh)
        # if thresh >= 0.5:
        #     break


dispersion = str((1. - 2 * best_thresh) * 100)[:-2] + '%'
print(best_thresh)
ug.remove_edges_from(ug.edges())
for i in range(0, len(corpus_tfidf)):
    sim = index2[lsi_model2[corp[i]]]
    for j in range(i + 1, len(sim)):
        dist = (1. - sim[j]) / 2.
        if dist < best_thresh and j in ug and i in ug:
            ug.add_edge(i, j, {'weight': dist})
graphs = sorted(nx.connected_component_subgraphs(ug), key=len, reverse=True)
test = [x for x in graphs if 20 > len(x) >= 3]
exclude = [x.nodes() for x in graphs if x not in test]
for graph in test:
    print("\n CLUSTER: \n")
    for no in graph:
        try:
            print(ug.node[no]['title'], ug.node[no]['source'], no)
        except:
            pass
print("\n AND \n")


for no in list(set().union(*exclude)):
    try:
        print(ug.node[no]['title'], ug.node[no]['source'], no)
    except:
        pass
size = len(corp)

tg = nx.DiGraph()
tg.add_node(0, overall_size=size)

count_suggest = 1
count_comp = 1
big_list = []
small_list = []
keywords_in = ['ms', '.', 'cookies', 'cookie', 'mr', '_', '-', '2016']


graphx = sorted([[len(i), nx.average_clustering(i), i]
                 for i in test], reverse=True)  # 0:min(5,len(graphs)-1)]
# for i in range(min(6,len(graphs))):
#     ug.remove_nodes_from(graphs[i])


for a in graphx:
    comp = a[2]
    if len(comp) >= 3:
            # now for comp level keyword extraction
            # if len(comp) >= 7:
        all_words = []
        for i in comp:
            ug.node[i]['comp'] = count_comp
            ug.node[i]['single'] = 0
            for word in punc.sub('', ug.node[i]['title']).split(" "):
                # print word
                if word not in stop_words:
                    all_words.append(word)
        a = sorted([[len([b for b in all_words if b == word]), word]
                    for word in list(set(all_words))], reverse=True)
        if len(a) >= 2:
            keywords = a[0][1] + ", " + a[1][1]
        elif len(a) == 1:
            keywords = a[0][1]
            # keywords_in.append(keywords[0])
            # keywords_in.append(keywords[1])
        else:
            keywords = ''

        # clustering for detail view
        if nx.average_clustering(comp) == 1:
            clustering = 100
        else:
            clustering = str(nx.average_clustering(comp))[2:4]

        # compute the centrality to turn them into one detail view and the
        # radius size
        count_degree = 1
    # elif len(comp) in [4,5]:
        closeness = nx.closeness_centrality(comp, distance=True)
        # for [b,a] in sorted([[closeness[r],r] for r in comp.nodes()],
        # reverse=True):
        for (a, b) in sorted([[a, nx.degree(comp)[a]] for a in nx.degree(comp)], key=lambda close: close[1], reverse=True):
            ug.node[a]['deg'] = b
            ug.node[a]['deg_pos'] = float(count_degree) / len(comp) * 360
            count_degree += 1
        ordering = sorted(list(closeness.items()),
                          key=lambda close: close[1], reverse=True)
        susvec = ordering[0][0]
        cnode = ug.node[susvec]
        cnode['suggest'] = count_comp
        q = Suggest(custom=strin, title=ug.node[susvec]['title'], url=ug.node[susvec][
                    'url'], distance=count_comp, images=ug.node[susvec]['images'], keywords=keywords, source=ug.node[susvec]['source'])
        q.save()
        q = Suggest(title=ug.node[susvec]['title'], url=ug.node[susvec]['url'], rank=count_comp, images=ug.node[
                    susvec]['images'], keywords=keywords, source=ug.node[susvec]['source'])
        q.save()

        # add the nodes for the arc
        tg.add_node(count_comp, clustering=clustering, name=keywords)
        tg.add_edge(0, count_comp)

        tg.add_node(count_comp * 100, size=len(comp))
        tg.add_edge(count_comp, count_comp * 100)
        count_comp += 1
    else:

        ug.remove_nodes_from(comp)


# tg.add_edge(0,50)
# tg.add_node(5000, size= 0.1)
# tg.add_edge(50,5000)
# tg.node[0]['final_size']=len(ug.nodes())
# tg.node[0]['comps'] = count_comp-1
# #tg.node[0]['thresh'] = best_thresh
# #tg2.node[0]['final_size']=len(ug.nodes())
# tg.node[0]['comps'] = count_comp-1
# #tg2.node[0]['thresh'] = best_thresh
# ug.graph['size']=len(ug.nodes())
# ug.graph['comps'] = count_comp-1
# ug.graph['senders'] = senders
# ug.graph['thresh'] = best_thresh
# ug.graph['dispersion'] = dispersion
# #ug.graph['tech-nontech-ratio'] = str(tech_ratio)#str(len(doc)/float(articlenumber))#
# ug.graph['wordcount'] = str(words)
# ug.graph['links'] = str(no_urls)
# ug.graph['articlenumber'] = str(articlenumber)

# export
# ug_nl = json_graph.node_link_data(ug)
# tgt = json_graph.tree_data(tg,root=0)
# #tgt_mobile = json_graph.tree_data(tg2,root=0)
# with open('nh/static/nh/json/' + date.today().isoformat() + '_center.json', 'w+') as fp:
#     json.dump(tgt,fp)

# with open('nh/static/nh/json/' + date.today().isoformat() + '_graph.json', 'w+') as fp:
#     json.dump(ug,fp)


# q = Query.objects.filter(string= strin)
# for query in q:
#     query.articlenumber = articlenumber
#     query.words = words
#     query.save()

#send_mail('successful update', 'Successful update. headlines are:' , 'grphtcontact@gmail.com', ['pvboes@gmail.com'])
