import re
from nltk.corpus import stopwords
from scope.methods.semantics import stopwords as stopw


class PreProcessing():
    """docstring for PreProcessing."""

    def __init__(self, lang, nlp):
        self.nlp = nlp

        if lang == "en":
            self.stopwords = stopw.EN
            self.noun_tags = ["NN", "NNS", "NNP", "NNPS"]
            self.key_deps = ["acomp", "ccomp", "pcomp", "xcomp", "relcl", "conj"]
        elif lang == "de":
            self.stopwords = stopwords.words('german')
            self.noun_tags = ["NE", "NN", "NNE"]
            self.key_deps = ["nk", "sb", "cc", "cp", "cj"]
        else:
            raise Exception("Language not known.")

    def prepare_sentences(self, articles):
        total = [a.body for a in articles]

        # Convert text to spacy object
        docs = [self.nlp(t) for t in total]

        sents = []
        original_sents = []

        for doc in docs:
            for sent in doc.sents:
                if sent.text[-1] in ["?", ".", "!"]:
                    token_sent = self._noun_token_sent(sent)

                    sents.append(token_sent)
                    original_sents.append(sent.text)

        return sents, original_sents

    def _generate_clean_docs(self, texts):
        docs = [self.nlp(re.sub(r" {2,}", " ", re.sub(r"[^\w\s\.,!?]", " ", a).replace("_", " ")).strip()) for a in texts]

        return docs

    def _noun_token_sent(self, sent):
        temp = []
        for t in sent:
            if re.findall(r"\b[12][0-9]{3}\b", t.text):
                temp.append("-DATE-")
            elif t.like_email:
                temp.append("-EMAIL-")
            elif t.like_url:
                temp.append("-URL-")
            elif t.like_num:
                temp.append("-NUMBER-")
            elif t.tag_ in self.noun_tags:
                temp.append(t.lemma_)

        return " ".join(list(set(temp)))

    def noun_based_preprocessing(self, articles):
        docs = [self.nlp(a.body) for a in articles]
        clean = []

        for doc in docs:
            for sent in doc.sents:
                token_sent = self._noun_token_sent(sent)

            clean.append(token_sent)
        return clean

    def keyword_preprocessing(self, articles, max_chunk_length=5):
        '''
            Grammar based text extraction from titles.

            articles: List of article objects
        '''
        # Merge body and title
        # total = [". ".join([a.title, a.body]) for a in articles]
        total = [a.title for a in articles]

        # Convert text to spacy object
        docs = self._generate_clean_docs(total)

        lemmas = []
        chunks = []
        clean = []

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
                    if t.ent_type_ and t.tag_ in self.noun_tags:
                        if len(c.text.split(" ")) <= max_chunk_length:
                            chunks.append(c.text.strip())
                            temp = []
                            for T in c.subtree:
                                if T.tag_ in self.noun_tags:
                                    temp.append(c.lemma_)
                            lemmas.append(" ".join(temp))
                            found = True
                            break

            # Search for all entities
            if not found:
                for c in doc.ents:
                    if len(c.text.split(" ")) <= max_chunk_length:
                        chunks.append(c.text.strip())
                        temp = []
                        for T in c.subtree:
                            if T.tag_ in self.noun_tags:
                                temp.append(c.lemma_)
                        lemmas.append(" ".join(temp))
                        found = True

            # Last resort - get all nouns
            if not found:
                for c in doc.noun_chunks:
                    if len(c.text.split(" ")) <= max_chunk_length:
                        for t in c.subtree:
                            if t.tag_ in self.noun_tags:
                                chunks.append(c.text.strip())
                                temp = []
                                for T in c.subtree:
                                    if T.tag_ in self.noun_tags:
                                        temp.append(c.lemma_)
                                lemmas.append(" ".join(temp))
                                break

        # Specific workaround for german chunks which start always with
        # a stopword
        for c in chunks:
            temp = c.lower().split(" ")
            orig = c.split(" ")

            if temp[0] in self.stopwords:
                orig.pop(0)

            clean.append(" ".join(orig))

        if len(clean) != len(lemmas):
            raise AttributeError("Sizes not equal!")

        return clean, lemmas
