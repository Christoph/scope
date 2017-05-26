import django
django.setup()

from tldextract import tldextract
from langdetect import detect

from scope.models import AgentImap, Agent, Source, Article
from scope.methods.semantics import document_embedding
from scope.methods.semantics import summarizer
from scope.methods.dataprovider import imap_handler

from scope.methods.graphs import clustering_methods
from curate.convenience import functions as helper


# initializations
customer_key = "commerzbank_germany"

target_clusters = 16
summary_max_len = 100

language_dict = {
    'ger': 'de',
    'eng': 'en',
}

# GET DATA
print("GET DATA")

customer, curate_customer, query, agentimap, language = helper.create_customer_from_config_file(customer_key)

# From mail
db_articles = []
mails = []

# Get all sources connected to the curate_customer
connector = Agent.objects.filter(
    product_customer_id=curate_customer.id)

for con in connector:
    print("============= New Agent ===============")
    if isinstance(con.agent_object, AgentImap):
        print("imap")
        imap = imap_handler.ImapHandler(con.agent_object, language)

        mails = imap.get_data_new()

for a in mails:
    source, created = Source.objects.get_or_create(
        url=a['source'],
        defaults={"name": tldextract.extract(a['source']).domain.title()})

    art, created = Article.objects.get_or_create(
        title=a['title'],
        url=a['url'],
        defaults={"source": source, "body": a['body'],
                  "images": a['images'], "pubdate": a['pubdate']})

    db_articles.append(art)

filtered_articles = db_articles

print(len(filtered_articles))

# semantic analysis
print("SEMANTIC ANALYSIS")

# Create embedding model
data_model = document_embedding.Embedding(language_dict[language], "grammar_svd", filtered_articles)

vecs = data_model.get_embedding_vectors()
sim = data_model.get_similarity_matrix()

# clustering
print("CLUSTERING")

selected_articles, cluster_articles = clustering_methods.get_clustering(filtered_articles, sim, vecs, target_clusters)

print("KEYWORDS & SUMMARY/REPRESENTATIVE")

representative_model = summarizer.Summarizer(language_dict[language])

words = representative_model.get_keywords(cluster_articles)
rep = representative_model.text_rank(cluster_articles, max_size=summary_max_len)

print("RESULTS")
out = []
for i in range(0, len(cluster_articles)):
    out.append({
        "central_title": cluster_articles[i][0].title,
        "keywords": words[i],
        "representative": rep[i]
        })
