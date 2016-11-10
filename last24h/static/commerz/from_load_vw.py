import networkx as nx
import gensim
import nltk
import re
import string
import json
import urllib
from networkx.readwrite import json_graph

from last24h.models import Suggest
        
def db_suggestions(graph,maxcount,filt= None):
    
    sug = sorted([[d['suggest'],n] for n,d in graph.nodes_iter(data=True)])
    for i in range (0, maxcount):
        q = Suggest(id = i, title = graph.node[sug[i][1]]['title'], url = graph.node[sug[i][1]]['url'], custom = 'None',summary = graph.node[sug[i][1]]['summary'] )
        q.save()

#load from gensim objects

dict = gensim.corpora.Dictionary.load('last24h/static/commerz/vw.dict')
corp = gensim.corpora.MmCorpus('last24h/static/commerz/vw.mm')
lsi_model = gensim.models.LsiModel.load('last24h/static/commerz/vw.lsi')
index = gensim.similarities.MatrixSimilarity.load('last24h/static/commerz/vw.index')
#corpus_tfidf = gensim.corpora.MmCorpus('/tmp/corpus_tf.mm')
data = json.loads(open('last24h/static/commerz/ug_vw.json').read())
ug = json_graph.node_link_graph(data)
#import json graph and assign from another graph
size= len(corp)


ug.remove_edges_from(ug.edges())


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
    ug.add_node(i,title=titles[i],url=urls[i],suggest=0, summary = summary[i],images = images[i], comp = 0,source= source,keywords='',sent =probs2[i])#,keywords=keywords[i])

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

    test = [x for x in graphs if 20> len(x) >= 3]
    exclude = [x.nodes() for x in graphs if x not in test]
    #test2 = [len(x) for x in test]
    if len(test) >= 2:
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
        #first take care of the time signatures of the articles for the detail view
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
        #         now = datetime.datetime.now().isoformat()
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
            #if type(ug.node[i]['time']) != type('string'):
            # ug.node[i]['time'] = ''
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
#tgt_mobile = json_graph.tree_data(tg2,root=0)
with open('last24h/static/commerz/tgt_vw.json', 'w+') as fp:
# with open('last24h/static/commerz/tgt_vw.json', 'w+') as fp:
    json.dump(tgt,fp)
# with open('last24h/static/last24h/cs/cs_'+ strin +'_tgt_mobile.json', 'w+') as fp:
#     json.dump(tgt_mobile,fp)
with open('last24h/static/commerz/ug_vw.json', 'w+') as fp:
# with open('last24h/static/commerz/ug_vw.json', 'w+') as fp:
    json.dump(ug_nl,fp)

#send_mail('successful update', 'Successful update. headlines are:' , 'grphtcontact@gmail.com', ['pvboes@gmail.com'])

