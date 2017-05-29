import networkx as nx


def on_average_clustering_global(
        db_articles, size_bound, sim, params):
    graph = nx.Graph()
    no = len(db_articles)

    for i in range(0, len(db_articles)):
        graph.add_node(i, title=db_articles[i].title)

    graph.remove_edges_from(graph.edges())
    for i in range(0, no):
        for j in range(i + 1, no):
            dist = (1. - sim[i, j])
            if dist < params["threshold"]:
                graph.add_edge(i, j, {'weight': dist})

    return _selection(graph, size_bound)

def on_average_clustering_test(
        db_articles, size_bound, sim, params, test):
    graph = nx.Graph()
    no = len(db_articles)

    for i in range(0, len(db_articles)):
        graph.add_node(i, title=db_articles[i].title)

    score_new = 0
    best_thresh = 0.
    best_score = 0
    for s in [x * params[0][2] for x in range(
            int(params[0][0] / params[0][2]),
            int(params[0][1] / params[0][2]))]:
        graph.remove_edges_from(graph.edges())
        for i in range(0, no):
            for j in range(i + 1, no):
                dist = (1. - sim[i, j])
                if dist < s:
                    graph.add_edge(i, j, {'weight': dist})
        structure = _selection(graph, size_bound)
        print(structure)
        score_new = test(structure, params[1])
        if score_new > best_score:
            best_score = score_new
            best_thresh = s

    graph.remove_edges_from(graph.edges())
    for i in range(0, no):
        for j in range(i + 1, no):
            dist = (1. - sim[i, j])
            if dist < best_thresh:
                graph.add_edge(i, j, {'weight': dist})

    return _selection(graph, size_bound), best_thresh

def _selection(graph, size_bound):
    clusters = sorted(nx.connected_component_subgraphs(
        graph), key=len, reverse=True)
    clustering = nx.average_clustering(graph)
    if isinstance(size_bound, list):
        cluster_list = sorted(
            [[len(i), nx.average_clustering(i), i]
             for i in clusters if (size_bound[0] <= len(i) <= size_bound[1])], reverse=True)
    else:
        cluster_list = sorted(
            [[len(i), nx.average_clustering(i), i]
             for i in clusters if size_bound <= len(i)], reverse=True)

    selection = {'no_clusters': len(cluster_list), 'no_articles': len(
        graph.nodes()), 'clustering': clustering, 'articles': []}
    for cluster in cluster_list:
        closeness = nx.closeness_centrality(cluster[2], distance=True)
        closeness_ordered = sorted(list(closeness.items()),
                                   key=lambda close: close[1], reverse=True)

        central_article = closeness_ordered[0][0]

        selection['articles'].append(
            [central_article, cluster[0], cluster[1]])
    return selection
