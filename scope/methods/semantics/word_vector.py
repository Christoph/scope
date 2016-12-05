import spacy
import numpy as np


class Model(object):
    """docstring for Model."""
    def __init__(self):
        pass

    def similarity(self, docs):
        sim = np.zeros([len(docs), len(docs)])

        for i in range(0, len(docs)):
            for j in range(i, len(docs)):
                sim[i, j] = docs[i].similarity(docs[j])
                sim[j, i] = sim[i, j]

        return sim
