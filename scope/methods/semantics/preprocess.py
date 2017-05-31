from nltk.corpus import stopwords
from scope.methods.semantics import stopwords as stopw


class PreProcessing():
    """docstring for PreProcessing."""

    def __init__(self, lang, nlp):
        self.nlp = nlp

        if lang == "en":
            self.stopwords = stopw.EN
            self.noun_tags = ["NN", "NNS", "NNP", "NNPS"]
        elif lang == "de":
            self.stopwords = stopwords.words('german')
            self.noun_tags = ["NE", "NN", "NNE"]
        else:
            raise Exception("Language not known.")

    def noun_based_preprocessing(self, articles):
        '''
            Grammar based text extraction using spacy.

            articles: list of article objects
        '''

        # Convert text to spacy object
        docs = [self.nlp(a.body) for a in articles]

        clean = []

        for doc in docs:
            temp = []

            for sent in doc.sents:
                for t in sent:
                    if t.tag_ in self.noun_tags:
                        temp.append(t.lemma_)

            clean.append(" ".join(temp))

        return clean
