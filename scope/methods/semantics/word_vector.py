import spacy
import numpy as np
import nltk


class Model(object):
    """docstring for Model."""
    def __init__(self, lang):
        print(lang)
        if(lang == "de"):
            self.stop_words = nltk.corpus.stopwords.words('german')

            self.pipeline = spacy.load("de")

            # Add german stopwords to spacy
            for word in self.stop_words:
                spacy.de.language_data.STOP_WORDS.add(word)

            # Set vocab entries of Stopwords to is_stop == true
            for word in spacy.de.language_data.STOP_WORDS:
                lexeme = self.pipeline.vocab[word.decode()]
                lexeme.is_stop = True

        if(lang == "en"):
            self.pipeline = spacy.load("en")

    def load_data(self, articles):
        docs = [d.body for d in articles]

        self.data = [self.pipeline(item) for item in docs]

    def similarity_matrix(self):
        sim = np.zeros([len(self.data), len(self.data)])

        for i in range(0, len(self.data)):
            for j in range(i, len(self.data)):
                sim[i, j] = self.data[i].similarity(self.data[j])
                sim[j, i] = sim[i, j]

        return sim

    def document_vectors(self):
        return [d.vector for d in self.data]
