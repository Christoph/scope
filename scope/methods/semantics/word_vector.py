import spacy
import numpy as np


class Model(object):
    """docstring for Model."""
    def __init__(self):
        pass

    def compute(self, data):
        pass

    def similarity(self, docs, index):
        sim = np.zeros(len(docs))

        for i in range(0, len(docs)):
            sim[i] = docs[index].similarity(docs[i])

        return sim
