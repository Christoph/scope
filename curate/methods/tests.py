class Curate_Test(object):
    """docstring for Curate_Test"""

    def __init__(self, test):
        super(Curate_Test, self).__init__()
        if test == 'clusters':
            self.test = clusters


def clusters(stats, weights):
    cluster_lengths = [i[0] for i in stats['articles']]
    weight_cluster_size = weights[0]
    weight_coverage = weights[1]
    return weight_cluster_size * stats['no_clusters'] + weight_coverage * sum(cluster_lengths) / stats['no_articles']
