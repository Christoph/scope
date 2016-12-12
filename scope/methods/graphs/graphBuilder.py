import networkx as nx


class Graph(object):
    """docstring for Graph."""

    def __init__(self, type):
        if type is "normal":
            self.graph = nx.Graph()

        if type is "di":
            self.graph = nx.DiGraph()

    def linkDataset(self, no):
        self.no = no

    def addNodes(self):
        self.graph.add_nodes_from(range(0, self.no))

    def addEdges_global_thresh(self, threshold, sim):
        self.graph.remove_edges_from(self.graph.edges())
        for i in range(0, self.no):
            for j in range(i + 1, self.no):
                dist = (1. - sim[i, j])
                if dist < threshold:
                    self.graph.add_edge(i, j, {'weight': dist})

    def addEdges_by_test(self, test, t, size_bound, sim):
        score_new = 0
        best_thresh = 0.
        best_score = 0
        for s in [x * t[0][2] for x in xrange(int(t[0][0] / t[0][2]), int(t[0][1] / t[0][2]))]:
            self.addEdges_global_thresh(s, sim)
            structure = self.central_articles(size_bound)
            score_new = test(structure, t[1])
            print structure
            print score_new
            if score_new > best_score:
                best_score = score_new
                best_thresh = s

        self.addEdges_global_thresh(best_thresh, sim)

    def central_articles(self, size_bound):

        clusters = sorted(nx.connected_component_subgraphs(
            self.graph), key=len, reverse=True)
        clustering = nx.average_clustering(self.graph)
        if isinstance(size_bound, list):
            cluster_list = sorted([[len(i), nx.average_clustering(i), i]
                                   for i in clusters if (size_bound[0] <= len(i) <= size_bound[1])], reverse=True)
        else:
            cluster_list = sorted([[len(i), nx.average_clustering(i), i]
                                   for i in clusters if size_bound <= len(i)], reverse=True)

        selection = {'no_clusters': len(cluster_list), 'no_articles': len(
            self.graph.nodes()), 'clustering': clustering, 'articles': []}
        for cluster in cluster_list:
            closeness = nx.closeness_centrality(cluster[2], distance=True)
            closeness_ordered = sorted(closeness.items(),
                                       key=lambda close: close[1], reverse=True)
            central_article = closeness_ordered[0][0]
            selection['articles'].append(
                [central_article, cluster[0], cluster[1]])

        return selection
