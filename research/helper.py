'''
Get data ready for clustering tests
'''

import json
import pandas as pd
import numpy as np

from nltk.metrics import edit_distance


# load 100088 articles
with open('er_data.json', 'r') as fp:
    data = json.load(fp)

# get top score label groups
for i, item in enumerate(d for d in data):
    for score in range(1, 6):
        temp = []

        # join all concepts with the same score
        for j, con in enumerate(d for d in item["concepts"]):
            if con["score"] == score:
                temp.append(con["label"]["eng"])

        # Create new item
        item[u"concepts_"+str(score)] = ",".join(temp)

    item[u"source_uri"] = item["source"]["uri"]
    item["title"] = item["title"].lower()

    # Remove old items
    item.pop("concepts", None)
    item.pop("source", None)

df = pd.DataFrame(data)

df["title"] = df["title"]
df["body"] = df["body"]
df = df.drop_duplicates(subset=['title'], keep=False)
df = df.drop_duplicates(subset=['body'], keep=False)

df.to_csv("articles.csv", index=False, encoding="utf-8")

'''
Group the data by concepts
'''

selected_column = "concepts_5"

temp = df[[selected_column, "wgt"]]
groups = temp.groupby(selected_column).count()
groups = groups.reset_index().reset_index()
groups.columns = ["label", selected_column, "count"]

# Set empty concept to 0
groups.loc[groups[selected_column] == "", "count"] = 0

df = df.join(groups.set_index(selected_column), on=selected_column)

# Select articles with certain properties
clustering = df[df["count"] > 5]
clustering = clustering[clustering["count"] < 20]
clustering = clustering[clustering[selected_column].str.len() < 60]
clustering = clustering.sort_values(by=selected_column)

clustering.to_csv("clustering_labeled.csv", index=False, encoding="utf-8")

'''
Find a clusters with high inter cluster difference by using edit
distance on the concepts.
'''

clustering = pd.read_csv("clustering_labeled.csv", encoding="utf-8")

labels = np.array(clustering.concepts_5.tolist())
testsets = []
avg_diff = []
clusters = 16

for i in range(0, 50):
    testsets.append(np.random.randint(len(labels), size=clusters))

sim_matrix = np.zeros([clusters, clusters])
vfunc = np.vectorize(edit_distance)

for test in testsets:
    for i in range(0, clusters):
        row = vfunc(labels[test], labels[test[i]])
        sim_matrix[i] = row

    avg_diff.append(sim_matrix.mean())

idx = np.array(avg_diff).argsort()[-1:]
chosen = labels[testsets[idx]]

small = clustering[clustering['concepts_5'].isin(chosen)]

small.to_csv(
    "clustering_" + str(clusters) + ".csv", index=False, encoding="utf-8")
