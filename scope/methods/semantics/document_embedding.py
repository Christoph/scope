''' Class which converts raw text into embeddings. '''
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from scope.methods.semantics import preprocess


class Embedding():
    """Create word embeddings."""

    def __init__(self, lang, nlp, model, articles):
        '''
            lang: Spacy language string (en, de, ...)
        '''

        self.lang = lang
        self.vecs = []
        self.sim = []
        self.nlp = nlp
        self.preprocessor = preprocess.PreProcessing(
            lang=self.lang,
            nlp=self.nlp)

        if model == "grammar_svd":
            self._create_svd_embeddings(articles)
        else:
            raise Exception("Model not known.")

    def _create_svd_embeddings(self, articles):
        '''
            Creates an SVD embedding.

            articles: List of Article objects

            return: Embedding vectors
        '''

        clean_text = self.preprocessor.lemmatize_text(articles)

        self._create_svd_embedding(clean_text)

    def _create_svd_embedding(self, clean_text):
        vectorizer = TfidfVectorizer(sublinear_tf=True)
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
