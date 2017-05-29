from curate.models import Curate_Query, Article_Curate_Query

def filter_bad_sources(curate_customer, incoming_articles,db=False):
    bad_sources = curate_customer.bad_source.all()
    outgoing_articles =[]
    if db is False:
        # the selection-made filter here is because the
        # oarticle_curate_objects fo these aticles have already been
        # created at this point
        queries = Curate_Query.objects.filter(
            curate_customer=curate_customer).filter(
                selection_made=True)

        relevant_article_titles = [i.article.title for i in Article_Curate_Query.objects.filter(
            curate_query__in=queries)]

        for a in incoming_articles:
            if a.source not in bad_sources and a.title not in relevant_article_titles:
                outgoing_articles.append(a)
            else:
                print("Filtered because bad source")
                print(a.title, a.source)
    else:
        for a in incoming_articles:
            if a.source not in bad_sources:
                outgoing_articles.append(a)
            else:
                print("Filtered because bad source")
                print(a.title, a.source)

    print("Number of articles after filtering")
    print(len(outgoing_articles))
    return outgoing_articles

def filter_bad_articles(curate_customer, incoming_articles):
    bad_articles = Article_Curate_Query.objects.filter(
        curate_query__curate_customer=curate_customer).filter(bad_article=True)

    outgoing_articles = []
    for a in incoming_articles:
        ma = min(len(a.title), 30)
        if not any([(a.title[0:ma] in bad.article.title) or (a.url == bad.article.url)for bad in bad_articles]):
            outgoing_articles.append(a)
        else: 
            print("Filtered because marked as bad article")
            print(a.title)

    return outgoing_articles
