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

    def prepare_sentences(self, cluster):
        docs = [self.nlp(a.body) for a in cluster]

        sents = []
        original_sents = []
        for doc in docs:
            for sent in doc.sents:
                temp = []

                for t in sent:
                    if t.tag_.find("NN") >= 0:
                        temp.append(t.lemma_)

                sents.append(" ".join(temp))
                original_sents.append(sent.text)

        return sents, original_sents

    def keyword_preprocessing(self, articles):
        '''
            Grammar based text extraction from titles.

            articles: List of article objects
        '''

        # Convert text to spacy object
        docs = [self.nlp(a.title) for a in articles]

        chunks = []

        for doc in docs:
            found = False

            '''
            Iterate over all noun chunks
            Check if the chunk contains any noun entities
            Check for any entity
            Check for any noun
            '''

            for c in doc.noun_chunks:
                for t in c.subtree:
                    if t.ent_type_ and t.tag_.find("NN") >= 0:
                        chunks.append(c.text)
                        found = True
                        break

            # Search for all entities
            if not found:
                for c in doc.ents:
                    chunks.append(c.text)
                    found = True

            # Last resort - get all nouns
            if not found:
                for c in doc.noun_chunks:
                    for t in c.subtree:
                        if t.tag_.find("NN") >= 0:
                            chunks.append(c.text)

        return chunks
