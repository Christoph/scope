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
        elif model == "grammar_wv":
            self._create_wv_embeddings(articles)
        else:
            raise Exception("Model not known.")

    def _create_svd_embeddings(self, articles):
        '''
            Creates an SVD embedding.

            articles: List of Article objects

            return: Embedding vectors
        '''

        clean_text = self.preprocessor.noun_based_preprocessing(articles)

        self._create_svd_embedding(clean_text)

    def _create_wv_embeddings(self, articles):
        '''
            Creates an SVD embedding.

            articles: List of Article objects

            return: Embedding vectors
        '''

        clean_text = self.preprocessor.noun_based_preprocessing(articles)

        self._create_wv_embedding(clean_text)

    def _create_svd_embedding(self, clean_text):
        vectorizer = TfidfVectorizer(sublinear_tf=False, ngram_range=(1, 1))
        tfidf = vectorizer.fit_transform(clean_text)

        # similarities
        dim = self._select_dimension(tfidf, 0.15)
        print("Selected Dimension: " + str(dim))

        self.vecs = TruncatedSVD(n_components=dim).fit_transform(tfidf)
        self.sim = cosine_similarity(self.vecs)

    def _select_dimension(self, tfidf, target_variance):
        initial_dim = 70
        svd = TruncatedSVD(n_components=initial_dim).fit(tfidf)

        var = sum(svd.explained_variance_)
        dim = initial_dim - 1

        if var >= target_variance:
            while var >= target_variance:
                dim = dim - 1
                var = sum(svd.explained_variance_[0:dim])
            return dim + 1

        if var < target_variance:
            while var < target_variance:
                dim = dim + 1
                if dim >= initial_dim:
                    initial_dim = int(initial_dim * 1.5)
                    svd = TruncatedSVD(n_components=initial_dim).fit(tfidf)
                var = sum(svd.explained_variance_[0:dim])
            return dim + 1

    def _create_wv_embedding(self, clean_text):
        docs = [self.nlp(text) for text in clean_text]
        vecs = []
        for doc in docs:
            vecs.append(doc.vector)

        # similarities
        self.vecs = vecs
        self.sim = cosine_similarity(self.vecs)

    def get_similarity_matrix(self):
        ''' Get the similarity matrix '''
        return self.sim

    def get_embedding_vectors(self):
        ''' Get the embedding vectors. '''
        return self.vecs
