from scope.methods.graphs.graphBuilder import Graph

class Selection(object):
    """docstring for Selection"""

    def __init__(self, db_articles, sim):
        self.graph = Graph("normal")
        self.db_articles = db_articles
        self.sim = sim

    def _create_graph(self):
        self.graph.linkDataset(len(self.db_articles))
        self.graph.addNodes(self.db_articles)

    def by_clustering(self, clustering):
        self._create_graph()
        return self.graph.addEdges_clustering(self.sim, clustering)

    def global_thresh(self, threshold, size_bound):
        self._create_graph()
        self.graph.addEdges_global_thresh(threshold, self.sim)
        return self.graph.central_articles(size_bound)

    def by_test(self, test, params, size_bound):
        self._create_graph()
        self.graph.addEdges_by_test(test, params, size_bound, self.sim)
        return self.graph.central_articles(size_bound)
