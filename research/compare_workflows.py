import numpy as np
import pandas as pd

import research.compare_workflow_functions as funcs

# always reload other scripts
reload(funcs)

data = funcs.preprocess(True)
stats = pd.DataFrame(columns=["similarity_type", "dimension", "n_articles", "articles"])

dimensions = [10,20,30,40,50]

for i, dim in enumerate(dimensions):
    similarities = funcs.semantic_analysis(data, dim)

    for j, (key, value) in enumerate(similarities.iteritems(), 1):
        print i*len(similarities)+j
        articles = funcs.compute_clusterings(value, data)

        stats.loc[i*len(similarities)+j] = [key, dim, len(articles), articles]

stats.to_csv("stats.csv", index=False)
