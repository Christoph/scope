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
    lower_cluster_bound = weights[2]
    upper_cluster_bound = weights[3]
    if stats['no_clusters'] not in range(int(lower_cluster_bound),int(upper_cluster_bound)):
        return 0
    return weight_cluster_size * stats['no_clusters'] + weight_coverage * sum(cluster_lengths) / stats['no_articles'] 