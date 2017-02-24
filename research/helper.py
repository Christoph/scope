import pandas as pd
import numpy as np
import json


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

df["title"] = df["title"].str.lower()
df = df.drop_duplicates(subset=['title'], keep=False)

df.to_csv("articles.csv", index=False, encoding="utf-8")

selected_column = "concepts_5"

temp = df[[selected_column, "wgt"]]
groups = temp.groupby(selected_column).count()
groups = groups.reset_index().reset_index()
groups.columns = ["label", selected_column, "count"]

# Set empty concept to 0
groups.loc[groups[selected_column] == "", "count"] = 0

df = df.join(groups.set_index(selected_column), on=selected_column)

clustering = df[df["count"]>5]
clustering = clustering[clustering["count"] < 20]
clustering = clustering[clustering[selected_column].str.len() > 40]
clustering = clustering.sort_values(by=selected_column)

clustering.to_csv("clustering_labeled.csv", index=False, encoding="utf-8")
