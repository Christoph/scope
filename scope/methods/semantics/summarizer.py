from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy import stats
import numpy as np
import re

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

    def create_sample_text(self, text, max_length):
        doc = self.nlp(re.sub(r" {2,}", " ", re.sub(r"[^\w\s\.,!?#]", " ", text).replace("_", " ")).strip())

        temp = []
        for sent in doc.sents:
            if sent.text.strip()[-1] in ["?", ".", "!"]:
                if len(" ".join(temp) + " " + sent.text) > max_length:
                    break
                temp.append(sent.text.strip())
            # else:
            #     print(sent.text)

        return " ".join(temp)

    def text_rank(self, cluster_articles, central_articles, max_length):
        summaries = []

        for art in central_articles:
            cluster = cluster_articles[art]

            vectorizer = TfidfVectorizer(sublinear_tf=True)
            summary_text = ""

            sents, original_sents = self.preprocessor.prepare_sentences(
                cluster)

            # Normalize
            normalized_matrix = vectorizer.fit_transform(sents)

            # Similarity Graph
            sim = cosine_similarity(normalized_matrix)

            # Create graph
            graph = nx.from_numpy_matrix(sim)

            # Pagerank sentences
            scores = nx.pagerank(graph)
            text_lengths = [len(s) for s in original_sents]

            tokens = [len(s.split(" ")) for s in original_sents]
            indices = np.where(np.array(tokens) >= 3)[0]

            groups = []
            for i in range(0, len(indices)):
                summary = []
                length = 0
                score = []

                for j in range(i, len(indices)):
                    ind = indices[j]
                    if length + text_lengths[ind] > max_length:
                        break

                    if original_sents[ind] in art.body and original_sents[ind] not in summary:
                        length += text_lengths[ind]
                        summary.append(ind)
                        score.append(scores[ind])

                if score:
                    mean_score = np.mean(score)
                    groups.append((summary, mean_score))

            ranked = sorted(groups, key=lambda tup: tup[1], reverse=True)

            for i in ranked[0][0]:
                summary_text = summary_text + " " + original_sents[i]

            # # Ranked sentences
            # ranked_clean = sorted(((scores[i], s) for i, s in
            #                        enumerate(sents)),
            #                       reverse=True)
            #
            # ranked = sorted(((scores[i], s) for i, s in enumerate(original_sents)),
            #                 reverse=True)
            #
            # # Prepare variables
            # token_sets = [set(s[1].split(" ")) for s in ranked_clean]
            # text_lengths = [len(s[1]) for s in ranked]
            #
            # # Selection
            # ind = self._get_summary_indices(token_sets, text_lengths, max_length)
            #
            # for i in ind:
            #     summary = summary + " " + ranked[i][1]
            #

            summaries.append(summary_text.strip())

        return summaries

    def _get_summary_indices(self, tokens, lengths, max_len):

        # Use only 25th to 75th percentile
        lengths = np.array(lengths)
        indices = np.where(np.logical_and(lengths <= np.percentile(lengths, 75), lengths >= np.percentile(lengths, 10)))

        total_length = 0
        total_tokens = set([])
        sents = []

        for i in indices[0]:
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
        return (len(a.union(b)) - len(a.intersection(b))) / len(a.union(b))

    def _get_top_words(self, ranked, center, n_words, max_characters):

        words = []
        total_tokens = set("")

        for i in range(0, int(len(ranked))):
            tokens = set(ranked[i].lower().split(" "))

            if self._jaccard_dist(total_tokens, tokens) > 0.8:
                if ranked[i] in center.body:
                    if len(words) >= n_words:
                        break

                    if len(" ".join(words)+" "+ranked[i]) <= max_characters:
                        total_tokens = total_tokens.union(tokens)
                        words.append(ranked[i])

        return words

    def get_keywords(self, clusters, selected_articles, n_words, max_characters):
        keywords = []
        for center in selected_articles:
            clust = clusters[center]
            chunks, lemmas = self.preprocessor.keyword_preprocessing(clust)

            docs = [self.nlp(t) for t in chunks]
            normalized_matrix = []

            for doc in docs:
                normalized_matrix.append(doc.vector)

            # Similarity Graph
            sim = cosine_similarity(normalized_matrix)

            # Create graph
            graph = nx.from_numpy_matrix(sim)

            # Pagerank sentences
            scores = nx.pagerank(graph)

            # Ranked sentences
            ranked = sorted(((scores[i], s) for i, s in
                             enumerate(chunks)),
                            reverse=True)

            keywords.append((center, self._get_top_words([r[1] for r in ranked], center, n_words, max_characters)))

        return dict(keywords)
