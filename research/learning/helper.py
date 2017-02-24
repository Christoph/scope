import django
django.setup()

import numpy as np
import pandas as pd

from scope.methods.dataprovider import er_handler
from scope.models import AgentEventRegistry

def save_articles(name, data):
    data.to_csv(name+".csv", index=False, encoding="utf-8")

def save_model(computed_model, name):
    '''
    Save model
    '''

    computed_model.save(name+"_model.h5")
    computed_model.save_weights(name+"_weights.h5")

def get_training_dataset(group_dict, size):
    pass

def get_labeld_er_data(keyword, timespan, number, label, blacklistDF, text_min_length=500):
    blacklist = blacklistDF.title.tolist()

    data = get_er_data(keyword, timespan, number, blacklist)

    labels = np.zeros(len(data), dtype=int) + label
    titles = [item["title"] for item in data]
    bodys = [item["body"] for item in data]

    raw = np.transpose([labels, titles, bodys])

    raw = pd.DataFrame(raw, columns=["label", "title", "text"])

    # Remove duplicates in title and text
    out = raw.drop_duplicates("title").drop_duplicates("text")

    # Remove short articles
    clean = out[out.apply(lambda x: len(x.text), axis=1) > 50]

    return clean

def get_er_data(keywords, timespan, number, blacklist, text_min_length=500):
    agent = AgentEventRegistry(
        user="christoph.kralj@gmail.com",
        pwd="XzbiyLnpeh8MBtC{$4hv",
        lang="eng",
        concepts=keywords,
        locations="")

    er = er_handler.EventRegistryHandler(agent)

    data = er.get_data_with_checks(timespan, number, blacklist, text_min_length)

    return data
