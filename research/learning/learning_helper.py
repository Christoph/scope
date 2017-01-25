'''
Helper function for learning data aquisition.
'''

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

    computed_model.save("curate/customers/"+name+"_model.h5")
    computed_model.save_weights("curate/customers/"+name+"_weights.h5")

def get_labeld_er_data(keyword, timespan, number):
    data = get_er_data(keyword, timespan, number)

    labels = np.zeros(len(data), dtype=int) + 1
    titles = [item["title"] for item in data]
    bodys = [item["body"] for item in data]

    raw = np.transpose([labels, titles, bodys])

    out = pd.DataFrame(raw, columns=[keyword, "title", "text"])

    return out

def get_er_data(keywords, timespan, number):
    agent = AgentEventRegistry(
        user="christoph.kralj@gmail.com",
        pwd="XzbiyLnpeh8MBtC{$4hv",
        lang="eng",
        concepts=keywords,
        locations="")

    er = er_handler.EventRegistryHandler(agent)

    data = er.get_data(timespan, number)

    return data
