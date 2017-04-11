import django
django.setup()

import numpy as np
import pandas as pd
from textblob import TextBlob
import re

from scope.research.semantics import hal_embedding

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF, TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity, rbf_kernel
from sklearn.preprocessing import MinMaxScaler

import spacy
import nltk

nlp = spacy.load("en")

reload(clustering_methods)
reload(hal_embedding)

# GET DATA
print "GET DATA"
db_articles = []
labels = []


data = pd.read_csv("clustering_16.csv", encoding="utf-8")

# rename labels
unique_labels = np.unique(data.label)
for i in range(1, len(unique_labels) + 1):
    data.ix[data.label == unique_labels[i - 1], "label"] = i

for a in data.iterrows():
    source = Source.objects.create(
        url=a[1]['url'][0:199], name=a[1]['url'][0:199])

    art = Article.objects.create(
        title=a[1]['title'],
        url=a[1]['url'],
        source=source,
        body=a[1]['body'],
        images=a[1]['image'],
        pubdate=a[1]['date'])

    db_articles.append(art)
    labels.append(a[1]["label"])

labels = np.array(labels)

print "articles:"
print len(db_articles)

filtered_articles = db_articles

# semantic analysis
print "SEMANTIC ANALYSIS"

texts = [TextBlob(a.body) for a in filtered_articles]

tags = [TextBlob(a.body).tags for a in filtered_articles]

parsed = [TextBlob(a.body).parse().split(" ") for a in filtered_articles]

text_np = []

for doc in parsed:
    t_np = []

    for word in doc:
        if word.find("B-NP") >= 0 or word.find("I-NP") >= 0:
            t_np.append(re.sub("/.*", "", word))

    text_np.append(" ".join(t_np))


docs = [nlp(a.body) for a in filtered_articles]

dep_labels = ["acomp", "ccomp", "pcomp", "xcomp", "csubj",
              "csubjpass", "dobj", "nsubj", "nsubjpass", "pobj"]

used_deps = ["acomp", "ccomp", "pcomp", "xcomp", "relcl", "conj"]
used_tags = ["NN", "NNS", "NNP", "NNPS"]

text_nnvb = []
text_lemma = []
text_checked = []

for doc in docs:
    temp = []
    lemma = []
    lemma_checked = []

    for sent in doc.sents:
        for t in sent:
            # if t.tag_ in used_tags or t.dep_ in used_deps:
            # if t.tag_.find("NN") >= 0 or t.dep_.find("comp") >= 0:
            if t.tag_.find("NN") >= 0:
                temp.append(t.lemma_)

            if t.like_email:
                lemma_checked.append("-EMAIL-")
            elif t.like_num:
                lemma_checked.append("-NUMBER-")
            elif t.like_url:
                lemma_checked.append("-URL-")
            else:
                lemma_checked.append(t.lemma_)

            lemma.append(t.lemma_)

    text_nnvb.append(" ".join(temp))
    text_lemma.append(" ".join(lemma))
    text_checked.append(" ".join(lemma_checked))


# Replace dollar
replaced = [re.sub("[\$]?[0-9]\d*(\.\d+)?(?![\d.])( \willion)",
                   "-CURRENCY-", t) for t in text_lemma]

# Replace euro/pounds
replaced = [re.sub("[0-9]\d*(\.\d+)?(?![\d.])( \willion)? (euros|pounds)+",
                   "-CURRENCY-", t) for t in replaced]

# Replace dates
replaced = [re.sub("\s[12][0-9]{3}\\b", " -DATE-", t) for t in replaced]

# Replace number
replaced = [re.sub("[+-.,]?[0-9.,]{2,}", " -NUMBER-", t) for t in replaced]

# Replace url
replaced = [re.sub('http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[:/?#\[\]@+\-\._~=]|[!$&\'()*+,;=]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                   " -URL-", t) for t in replaced]

replaced = [re.sub("[a-z]*\.[a-z]{2,3}", " -URL-", t) for t in replaced]

# HAL

contexts = ["opel"]

hal, vocab = hal_embedding.HAL(replaced)

hal_grammar, vocab_grammar, context_grammar = hal_embedding.HAL_context_grammar(
    [a.body for a in filtered_articles], contexts, nlp)

# SVD doesnt work with the pandas output
# if hal_grammar.shape[0] > 1000:
#     svd_grammar = TruncatedSVD(
#         n_components=100, random_state=1).fit_transform(hal_grammar)
# else:
    # svd_grammar = hal_grammar
svd_grammar = hal_grammar

sim_grammar = cosine_similarity(svd_grammar)

# Get context row
context_row = sim_grammar[vocab_grammar[contexts[0]]].copy()

# Remove self similarity and rescale
min_max_scaler = MinMaxScaler()

context_row[context_row >= 1.] = context_row.min() - 0.001
rescaled_grammar = min_max_scaler.fit_transform(context_row.reshape(-1, 1))

# Get similarity list
grammar_similarities = pd.DataFrame(
    {'word': sorted(vocab_grammar, key=vocab_grammar.get),
     'similarity': rescaled_grammar.flatten()
     })
grammar_similarities = grammar_similarities.sort_values(
    "similarity", ascending=False)
