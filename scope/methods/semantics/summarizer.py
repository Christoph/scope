from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy import stats

from scope.methods.semantics import preprocess

import networkx as nx


class Summarizer():
    """docstring for Summarizer."""

    def __init__(self, lang, nlp):
        '''
            nlp: Spacy instance
        '''

        self.nlp = nlp
        self.preprocessor = preprocess.PreProcessing(
            lang=lang,
            nlp=self.nlp)

    def text_rank(self, cluster_articles, max_size):
        summaries = []

        for clust in cluster_articles:
            vectorizer = TfidfVectorizer(sublinear_tf=True)
            summary = ""

            sents, original_sents = self.preprocessor.prepare_sentences(clust[1])

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

    def get_keywords(self, clusters):
        keywords = []

        for clust in clusters:
            chunks = self.preprocessor.keyword_preprocessing(clust[1])

            if chunks:
                keywords.append(stats.mode(chunks).mode[0])
            else:
                keywords.append("")

        return keywords
