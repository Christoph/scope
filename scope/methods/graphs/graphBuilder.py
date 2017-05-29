import networkx as nx
# import numpy as np
# import itertools
import logging

# from scope.methods.graphs import clustering_methods

logger = logging.getLogger('django')

class Graph(object):
    """docstring for Graph."""

    def __init__(self, type):
        if type is "normal":
            self.graph = nx.Graph()

        if type is "di":
            self.graph = nx.DiGraph()

    def linkDataset(self, no):
        self.no = no

    def addNodes(self, db_articles):
        for i in range(0, len(db_articles)):
            self.graph.add_node(i,title=db_articles[i].title)#add_nodes_from(range(0, self.no))

    # def addEdges_from_clustering(self, sim, clustering, params):
    #     self.graph.remove_edges_from(self.graph.edges())
    #
    #     if clustering == "affinity_propagation":
    #         labels, center_indices = self.clustering.affinity_propagation(sim)
    #     if clustering == "dbscan":
    #         threshold = params["threshold"]
    #         metric = params["metric"]
    #         algorithm = params["algorithm"]
    #         labels = clustering_methods.db_scan(sim, threshold, metric, algorithm)
    #     if clustering == "hierachical":
    #         vecs = params["vecs"]
    #         method = params["method"]
    #         metric = params["metric"]
    #         cluster_criterion = params["cluster_criterion"]
    #         cluster_threshold = params["cluster_threshold"]
    #         links, labels, c = clustering_methods.hierarchical_clustering(
    #             vecs, method, metric, cluster_criterion, cluster_threshold)
        #
        # # For each cluster
        # for i in range(0, len(center_indices)-1):
        #     elements = np.where(labels == i)[0]
        #     groups = list(itertools.permutations(elements, 2))
        #
        #     for edge in groups:
        #         dist = (1. - sim[edge[0], edge[1]])
        #         self.graph.add_edge(edge[0], edge[1], {'weight': dist})
        #
        # return center_indices

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
        for s in [x * t[0][2] for x in range(int(t[0][0] / t[0][2]), int(t[0][1] / t[0][2]))]:
            self.addEdges_global_thresh(s, sim)
            structure = self.central_articles(size_bound)
            score_new = test(structure, t[1])
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

            for node in cluster[2]:
                logger.debug(self.graph.node[node]['title'])
            logger.debug('and')
            closeness = nx.closeness_centrality(cluster[2], distance=True)
            closeness_ordered = sorted(list(closeness.items()),
                                       key=lambda close: close[1], reverse=True)

            central_article = closeness_ordered[0][0]
            
            selection['articles'].append(
                [central_article, cluster[0], cluster[1]])
        logger.debug("NEWCLUSTER")
        return selection
