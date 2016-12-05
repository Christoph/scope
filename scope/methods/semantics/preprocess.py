import re
import nltk
import string


class PreProcessing():
    """docstring for PreProcessing."""

    def __init__(self, lang):
        if(lang == "german"):
            self.stop_words = nltk.corpus.stopwords.words('german')
            self.stemmer = nltk.stem.snowball.GermanStemmer()

        if(lang == "english"):
            self.stop_words = nltk.corpus.stopwords.words('english')
            self.stemmer = nltk.stem.porter.PorterStemmer()

        self.punc = re.compile('[%s]' % re.escape(string.punctuation))

    def stemm(self, docs):
        # Remove punctuation, lower case everything and tokenize the docs
        term_vec = self._tokenize(docs)

        # Remove stop words from term vectors
        term_vec = self._removeStopwords(term_vec)

        # Stemming of all words using the porter stemmer
        term_vec = self._stemming(term_vec)

        return term_vec

    def _tokenize(self, doc):
        term_vec = []

        for d in doc:
            d = d.lower()
            # This might join two words if there is no additional space
            # TODO: Possible problem
            d = self.punc.sub('', d)
            term_vec.append(nltk.word_tokenize(d))

        return term_vec

    def _removeStopwords(self, term_vec):
        for i in range(0, len(term_vec)):
            term_list = []

            for term in term_vec[i]:
                if term not in self.stop_words:
                    term_list.append(term)

            term_vec[i] = term_list

        return term_vec

    def _stemming(self, term_vec):
        for i in range(0, len(term_vec)):
            for j in range(0, len(term_vec[i])):
                term_vec[i][j] = self.stemmer.stem(term_vec[i][j])
        return term_vec
