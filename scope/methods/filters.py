from scope.methods.dataprovider.blacklist import Blacklist


#this one is not actually in use at the moment
def remove_duplicate_articles_for_processing(self, incoming_articles):
    outgoing_articles = []
    title_list = list(set([article.title for article in incoming_articles]))
    for title in title_list:
        article_to_append = [article for article in incoming_articles if article.title == title]
        outgoing_articles.extend(article_to_append)

    return outgoing_articles

def blacklist_filter(article_dict):
	print "Now filtering by blacklists"
	blacklist = Blacklist()
	out = []
	for articles, newsletter in article_dict:
		out.append([blacklist.filter(articles),newsletter])
	return out

def remove_duplicate_articles_from_same_newsletter(article_dict): 
	print "Removing duplicates per newsletter"
	#this only works because of the redefined __eq__ and __hash__ methods of the SCopeNewsArticle class
	out = [[list(set(articles)),newsletter] for articles, newsletter in article_dict]
	# for articles, newsletter in article_dict:
		# out.append([)
		# article_list = []
		# for article in articles:
		# 	if not any([[(article.title in a.title) or (article.url == a.url)] for a in article_list]):
		# 		article_list.append(a)
		# out.append([article_list,newsletter])
	return out

