import django
django.setup()

import numpy as np

import imaplib
import email
import quopri
import urllib2
from urlparse import urlparse
from datetime import date, timedelta
from tldextract import tldextract

from scipy.cluster.hierarchy import linkage
from scipy.cluster.hierarchy import to_tree
from scipy.spatial.distance import pdist, squareform

from scope.models import Customer
from curate.models import Curate_Query, Article_Curate_Query
from curate.models import Curate_Customer
from scope.models import AgentImap, Agent, Source, Article
from scope.methods.dataprovider import news_handler
from scope.methods.dataprovider import url_extractor, constants

import scope.methods.semantics.preprocess as preprocess
import scope.methods.semantics.lsi as lsi
import scope.methods.semantics.word_vector as word_vector
from scope.methods.learning import binary_classifier
from scope.methods.graphs import clustering_methods
from scope.methods.graphs import selection_methods
import curate.methods.tests as tests

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF, TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity, rbf_kernel

from sklearn.cluster import AgglomerativeClustering

# initializations
customer_key = "neuland_herzer"
language = "eng"

db_articles = []
threshold = 0.0
wv_language_dict = {
    'ger': 'de',
    'eng': 'en',
}
lsi_language_dict = {
    'ger': 'german',
    'eng': 'english',
}
wv_model = word_vector.Model(wv_language_dict[language])
classifier = binary_classifier.binary_classifier(
    wv_model.pipeline, customer_key)

# GET DATA
print "GET DATA"

customer = Customer.objects.get(
    customer_key=customer_key)
curate_customer = Curate_Customer.objects.get(
    customer=customer)
query = query = Curate_Query.objects.create(
    curate_customer=curate_customer)

# From mail


def get_content(mail):
    contents = []

    if mail.is_multipart():
        # Walk over all parts
        for part in mail.walk():
            get_decoding(contents, part)
    else:
        get_decoding(contents, mail)

    return contents


def blacklist_comparison(blacklist, text):
    for item in blacklist:
        if text.find(item) >= 0:
            # print "Blacklisted"
            # print text

            return True
        else:
            return False


def get_decoding(contentsA, part):
    # Get content type
    ctype = part.get_content_type()
    # Get content encoding
    cenc = str(part.get('Content-Transfer-Encoding'))

    # Check if its text/plain and not text/html or multipart
    if ctype == 'text/plain':
        if cenc == 'quoted-printable':
            print "is MIME encoded"
            # If MIME encoded - decode and add
            contentsA.append(part.get_payload(decode=True))
        elif cenc == 'base64':
            print "is base64 encoded"
            contentsA.append(part.get_payload(decode=True))
        else:
            print "is not MIME encoded"
            # Else - add without decoding
            contentsA.append(part.get_payload())


connector = Agent.objects.filter(
    product_customer_id=curate_customer.id)

agent = connector[0].agent_object

url_extractor = url_extractor.Extractor()
mail_user = agent.user.encode("utf-8")
mail_pwd = agent.pwd.encode("utf-8")
mail_link = agent.imap.encode("utf-8")
mail_box = agent.mailbox.encode("utf-8")
mail_interval = agent.interval

news = news_handler.NewsSourceHandler()

out = []
filtered = []

# Connect to Mailbox
mailbox = imaplib.IMAP4_SSL(mail_link)
mailbox.login(mail_user, mail_pwd)
mailbox.select(mail_box)

# Get all mails from the last interval hours
if date.today().strftime('%w') == "1":
    yesterday = date.today() - timedelta(hours=mail_interval) - timedelta(days=2)
else:
    yesterday = date.today() - timedelta(hours=mail_interval)

# you could filter using the IMAP rules here (check
# http://www.example-code.com/csharp/imap-search-critera.asp)
resp, items = mailbox.search(
    None, '(SINCE "' + yesterday.strftime("%d-%b-%Y") + '")')
items = items[0].split()  # getting the mails ids

all_urls = []

# Get the whole mail content
for emailid in items:
    try:
    # fetching the mail, "`(RFC822)`" means "get the whole stuff",
    # but you can ask for headers only, etc
        resp, data = mailbox.fetch(emailid, "(RFC822)")

        email_body = data[0][1]  # getting the mail content

        # Convert to mail object

        mail = email.message_from_string(email_body)

        # All mail text/plain contents
        contents = get_content(mail)

        # Add urls from each content
        for content in contents:
            all_urls.extend(
                url_extractor.get_urls_from_string(content))
    except:
        pass
# Remove duplicates over different newsletters
all_urls = list(set(all_urls))
short = []

articles = news.get_articles_from_list(all_urls, language)

for article in articles:
    if article.title not in constants.EXCLUDE and not blacklist_comparison(constants.TITLE_BLACKLIST, article.title) and not blacklist_comparison(constants.TEXT_BLACKLIST, article.text) and len(article.text) > 0:
            if len(article.text) > 500:
                out.append({
                    "body": article.text, "title": article.title,
                    "url": article.url, "images": article.top_image,
                    "source": urlparse(article.url).netloc,
                    "pubdate": article.publish_date})
            else:
                short.append(article)
    else:
        filtered.append(article)

print "filtered articles"
print len(filtered)
print "too short articles"
print len(short)

all_articles = []

# Save the articles into the database
for a in out:
    try:
        # Check if source already exists
        source, created = Source.objects.get_or_create(
            url=a['source'],
            defaults={"name": tldextract.extract(a['source']).domain.title()})

        art, created = Article.objects.get_or_create(
            title=a['title'],
            url=a['url'],
            defaults={"source": source, "body": a['body'],
                      "images": a['images'], "pubdate": a['pubdate']})

        Article_Curate_Query.objects.create(
            article=art, curate_query=query, agent=connector[0])

        all_articles.append(art)

    except:
        print "Validation Error"
        continue

bad_sources = curate_customer.bad_source.all()

# check if duplicate titles exist and remove them
titles = [a.title for a in all_articles]
u, indices = np.unique(titles, return_index=True)
all_articles = np.array(all_articles)[indices]
all_articles = all_articles.tolist()

for a in all_articles:
    if a.source not in bad_sources:
        db_articles.append(a)

print "articles:"
print len(db_articles)

words = sum([len(i.body) for i in db_articles])

# CLASSIFY
print "CLASSIFY"
min_count = 100
classifier_type = "none"  # none, nn300

if classifier_type == "nn300":
    filtered_articles = classifier.classify_by_count(
        db_articles, min_count)
else:
    print "no classifier selected"
    filtered_articles = db_articles

print "articles after classification"
print len(filtered_articles)

# semantic analysis
print "SEMANTIC ANALYSIS"
lsi_dim = 20

pre = preprocess.PreProcessing(lsi_language_dict[language])
lsi_model = lsi.Model()

vecs = pre.stemm([a.body for a in filtered_articles])
lsi_model.compute(vecs, lsi_dim)

sim = lsi_model.similarity()

# test three different dim reduction methods
vectorizer = TfidfVectorizer(
    sublinear_tf=True, stop_words='english', max_df=0.9)
tfidf = vectorizer.fit_transform([a.body for a in filtered_articles])

# similarities
svd = TruncatedSVD(n_components=10, random_state=1).fit_transform(tfidf)
sim_svd = cosine_similarity(svd)

# clustering
print "CLUSTERING"
print "test ER as validation field"

# params
params_custom = [[0.001, 0.45, 0.001], [1, 0.01, 1, 15]]
params_svd = [[0.6, 0.9, 0.001], [1, 0.01, 1, 15]]

# used params
size_bound = [2, 18]
test = tests.Curate_Test("clusters").test

used_sim = sim_svd
used_params = params_svd

# custom classic
selection_custom_classic, threshold_classic = selection_methods.on_average_clustering_test(
    filtered_articles, size_bound, sim, params_custom, test)

labels_custom_classic = clustering_methods.sim_based_threshold(used_sim, threshold)
center_indices_custom_classic = [i[0] for i in selection_custom_classic['articles']]

selected_articles_custom = [
    filtered_articles[i] for i in center_indices_custom_classic]

print "custom classic"
print clustering_methods.internal_measure(svd, labels_custom_classic)

# custom
selection_custom, threshold = selection_methods.on_average_clustering_test(
    filtered_articles, size_bound, used_sim, used_params, test)

labels_custom = clustering_methods.sim_based_threshold(used_sim, threshold)
center_indices_custom = [i[0] for i in selection_custom['articles']]

selected_articles_custom = [
    filtered_articles[i] for i in center_indices_custom]

print "custom"
print clustering_methods.internal_measure(svd, labels_custom)

# affinity
labels_affinity, center_indices_affinity = clustering_methods.affinity_propagation(used_sim)

selected_articles_affinity = np.array(filtered_articles)[
    center_indices_affinity]

print "affinity"
print clustering_methods.internal_measure(svd, labels_affinity)

# gauss
labels_gauss = clustering_methods.bayes_gauss_mix(svd, components=10)

print "gauss"
print clustering_methods.internal_measure(svd, labels_gauss)

# hierachical
links_hc_ward, labels_hc_ward = clustering_methods.hierarchical_clustering(svd, "ward", "euclidean", "maxclust", 12)

print "hc ward"
print clustering_methods.internal_measure(svd, labels_hc_ward)

links_ward = linkage(svd, "ward", "euclidean")
links_cos = linkage(svd, "average", "cosine")

# hc merge function
ward_tree = to_tree(links_ward)
cos_tree = to_tree(links_cos)

# tree.pre_order() gives original indicies
# tree.dist gives distance of current index
# tree.count gives leave nodes below current point

# Subtree
sub = ward_tree.left.pre_order()

# All distances within the subtree
distance_vector = pdist(svd[sub])

# convert to squareform
distance_matrix = squareform(distance_vector)

# Get element with lowest mean distance
center = np.mean(distance_matrix, axis=1).argmin()
center_index = sub[center]
