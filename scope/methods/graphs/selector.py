from scope.methods.graphs.graphBuilder import Graph

class Selection(object):
    """docstring for Selection"""

    def __init__(self, no, sim):
        self.graph = Graph("normal")
        self.no = no
        self.sim = sim

    def _create_graph(self):
        self.graph.linkDataset(self.no)
        self.graph.addNodes()

    def global_thresh(self, threshold, size_bound):
        self._create_graph()
        self.graph.addEdges_global_thresh(threshold, self.sim)
        return self.graph.central_articles(size_bound)

    def by_test(self, test, params, size_bound):
        self._create_graph()
        self.graph.addEdges_by_test(test, params, size_bound, self.sim)
        return self.graph.central_articles(size_bound)
