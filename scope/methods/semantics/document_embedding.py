''' Class which converts raw text into embeddings. '''

import spacy

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from scope.methods.semantics import stopwords as stopw


class Embedding():
    """Create word embeddings."""

    def __init__(self, lang, model, articles):
        '''
            lang: Spacy language string (en, de, ...)
        '''

        self.lang = lang
        self.vecs = []
        self.sim = []

        if lang == "en":
            self.stopwords = stopw.EN
        elif lang == "de":
            self.stopwords = stopwords.words('german')
        else:
            raise Exception("Language not known.")

        if model == "grammar_svd":
            self._create_grammer_svd_embeddings(articles)
        else:
            raise Exception("Model not known.")

    def _create_grammer_svd_embeddings(self, articles):
        '''
            Creates an SVD embedding.

            articles: List of Article objects

            return: Embedding vectors
        '''

        clean_text = self._gammar_based_preprocessing(articles)

        self._create_svd_embedding(clean_text)

    def _gammar_based_preprocessing(self, articles):
        '''
            Grammar based text extraction using spacy.

            articles: list of article objects
        '''

        nlp = spacy.load(self.lang)

        # Convert text to spacy object
        docs = [nlp(a.body) for a in articles]

        clean = []

        for doc in docs:
            temp = []

            for sent in doc.sents:
                for t in sent:
                    if t.tag_.find("NN") >= 0:
                        temp.append(t.lemma_)

            clean.append(" ".join(temp))

        return clean

    def _create_svd_embedding(self, clean_text):
        vectorizer = TfidfVectorizer(
            sublinear_tf=True, stop_words=self.stopwords, strip_accents="unicode")
        tfidf = vectorizer.fit_transform(clean_text)

        # similarities
        self.vecs = TruncatedSVD(n_components=18).fit_transform(tfidf)
        self.sim = cosine_similarity(self.vecs)

    def get_similarity_matrix(self):
        ''' Get the similarity matrix '''
        return self.sim

    def get_embedding_vectors(self):
        ''' Get the embedding vectors. '''
        return self.vecs
