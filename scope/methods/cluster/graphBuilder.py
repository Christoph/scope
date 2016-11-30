import networkx as nx
from datetime import date, timedelta, datetime
from time import mktime
from random import randint

import dataprovider.constants as constants
import semantics.lsi as lsi
import semantics.word_vector as word_vector

reload(constants)
reload(lsi)
reload(word_vector)

lsi_model = lsi.Model()
wv_model = word_vector.Model()

class Graph(object):
    """docstring for Graph."""
    def __init__(self, type):
        if type is "normal":
            self.graph = nx.Graph()

        if type is "di":
            self.graph = nx.DiGraph()

    def linkDataset(self, data):
        self.data = data

    def addNodes(self):
        counter_add = 0

        for a in self.data:
            # dist_dict = classifier.prob_classify(word_feats(a['body'].split()))
            tup = tuple([int(j) for j in tuple(a['date'].split(
                '-') + a['time'].split(':')) + (0, 1, -1)])
            art_time = datetime.fromtimestamp(mktime(tup))
            self.graph.add_node(counter_add, title=a['title'], url=a['url'], suggest=0, summary=a['body'][0:400], images=a['image'], comp=0, source=a['source']['title'], keywords='', time=art_time, sent=randint(0, 100) / 100.)
            # sent =dist_dict.prob("pos"))
            counter_add += 1

    def addEdges(self, threshold):
        for i in range(0, len(self.data)):
            # sim = lsi_model.similarity(i)
            sim = wv_model.similarity(docs, i)
            for j in range(i + 1, len(sim)):
                dist = (1. - sim[j]) / 2.
                if dist < thresh:
                    self.graph.add_edge(i, j, {'weight': dist})
