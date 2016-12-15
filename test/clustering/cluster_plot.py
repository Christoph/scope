from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram


def plot_data(X):
    plt.figure(figsize=(10, 8))
    plt.scatter(X[:, 0], X[:, 1])
    plt.show()


def plot_clustering(X, labels):
    plt.figure(figsize=(10, 8))
    # plot points with cluster dependent colors
    plt.scatter(X[:, 0], X[:, 1], c=labels)
    plt.show()


def plot_clustering_with_center(X, labels, center):
    plt.figure(figsize=(10, 8))
    # plot points with cluster dependent colors
    plt.scatter(X[:, 0], X[:, 1], c=labels)
    plt.scatter(X[center, 0], X[center, 1], c='r',
                marker='x', s=100, linewidth='5')
    plt.show()

def fancy_dendrogram(*args, **kwargs):
    max_d = kwargs.pop('max_d', None)
    if max_d and 'color_threshold' not in kwargs:
        kwargs['color_threshold'] = max_d
    annotate_above = kwargs.pop('annotate_above', 0)

    ddata = dendrogram(*args, **kwargs)

    if not kwargs.get('no_plot', False):
        plt.title('Hierarchical Clustering Dendrogram (truncated)')
        plt.xlabel('sample index or (cluster size)')
        plt.ylabel('distance')
        for i, d, c in zip(ddata['icoord'], ddata['dcoord'],
                           ddata['color_list']):
            x = 0.5 * sum(i[1:3])
            y = d[1]
            if y > annotate_above:
                plt.plot(x, y, 'o', c=c)
                plt.annotate("%.3g" % y, (x, y), xytext=(0, -5),
                             textcoords='offset points',
                             va='top', ha='center')
        if max_d:
            plt.axhline(y=max_d, c='k')
    return ddata

def plot_dendrogram(link, truncation):
    fancy_dendrogram(
        link,
        truncate_mode='lastp',
        p=truncation,
        leaf_rotation=90.,
        leaf_font_size=12.,
        show_contracted=True,
        annotate_above=10,
    )
    plt.show()