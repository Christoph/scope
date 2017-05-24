import spacy

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy import stats

import networkx as nx


class Summarizer():
    """docstring for Summarizer."""

    def __init__(self, lang):
        '''
            lang: Spacy language string (en, de, ...)
        '''

        self.lang = lang
        self.nlp = spacy.load(self.lang)

    def text_rank(self, cluster_articles, max_size):
        summaries = []

        for clust in cluster_articles:
            vectorizer = TfidfVectorizer(sublinear_tf=True, strip_accents="unicode")
            docs = [self.nlp(a.body) for a in clust[1]]
            summary = ""

            sents, original_sents = self._prepare_sentences(docs)

            # Normalize
            normalized_matrix = vectorizer.fit_transform(sents)

            # Similarity Graph
            sim = cosine_similarity(normalized_matrix)

            # Create graph
            graph = nx.from_numpy_matrix(sim)

            # Pagerank sentences
            scores = nx.pagerank(graph)

            # Ranked sentences
            ranked_clean = sorted(((scores[i], s) for i, s in
                                   enumerate(sents)),
                                  reverse=True)

            ranked = sorted(((scores[i], s) for i, s in enumerate(original_sents)),
                            reverse=True)

            # Prepare variables
            token_sets = [set(s[1].split(" ")) for s in ranked_clean]
            text_lengths = [len(s[1].split(" ")) for s in ranked]

            # Selection
            ind = self._get_summary_indices(token_sets, text_lengths, max_size)

            for i in ind:
                summary = summary + " " + ranked[i][1]

            summaries.append(summary.strip())

        return summaries

    def _get_summary_indices(self, tokens, lengths, max_len):
        total_length = lengths[0]
        total_tokens = tokens[0]
        sents = [0]

        for i in range(1, int(len(tokens)*0.1)):
            if self._jaccard_dist(total_tokens, tokens[i]) > 0.8:
                temp = total_length + lengths[i]

                if temp >= max_len:
                    if total_length <= max_len * 0.5:
                        continue
                    else:
                        break

                total_length += lengths[i]
                total_tokens = total_tokens.union(tokens[i])
                sents.append(i)

        return sents

    def _jaccard_dist(self, a, b):
        return (len(a.union(b)) - len(a.intersection(b)))/len(a.union(b))

    def _prepare_sentences(self, docs):
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

    def _keyword_preprocessing(self, articles):
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
            Check if the chunk contains an entity which is a noun
            If yes add it and skip further extraction steps
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

    def get_keywords_from_clusters(self, clusters):
        keywords = []

        for clust in clusters:
            chunks = self._keyword_preprocessing(clust[1])

            keywords.append(stats.mode(chunks).mode[0])

        return keywords
