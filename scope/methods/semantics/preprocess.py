import re
import nltk
import string
import nltk
import spacy
import sys


class PreProcessing():
    """docstring for PreProcessing."""

    def __init__(self, lang):
        reload(sys)
        sys.setdefaultencoding('utf8')
        if(lang == "german"):
            self.stop_words = nltk.corpus.stopwords.words('german')
            self.stemmer = nltk.stem.snowball.GermanStemmer()
            self.pipeline = spacy.load("de")

            # Add stopwords to spacy
            for word in self.stop_words:
                spacy.de.language_data.STOP_WORDS.add(word)

            # Set vocab entries of Stopwords to is_stop == true
            for word in spacy.de.language_data.STOP_WORDS:
                lexeme = self.pipeline.vocab[word.decode()]
                lexeme.is_stop = True

        if(lang == "english"):
            self.stop_words = nltk.corpus.stopwords.words('english')
            self.stemmer = nltk.stem.porter.PorterStemmer()
            self.pipeline = spacy.load("en")

        self.punc = re.compile('[%s]' % re.escape(string.punctuation))

    def stemm(self, docs):
        # Remove punctuation, lower case everything and tokenize the docs
        term_vec = self._tokenize(docs)

        # Remove stop words from term vectors
        term_vec = self._removeStopwords(term_vec)

        # Stemming of all words using the porter stemmer
        term_vec = self._stemming(term_vec)

        return term_vec

    def lemma(self, docs):
        # Initialize output
        vectors = []

        # Import data into the spacy pipeline
        data = [self.pipeline(item) for item in docs]

        for doc in data:
            vectors.append([tok.lemma_ for tok in doc if (tok.is_digit or tok.is_alpha) and not tok.is_stop])

        return vectors, data

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
