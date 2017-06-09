import string
from nltk.corpus import stopwords
from scope.methods.semantics import stopwords as stopw
import re

def keywords_from_articles(cluster_articles, selected_articles, lang):
	if lang == "en":
		stop_words = stopw.EN
	elif lang == "de":
		stop_words = stopwords.words('german')

	punc = re.compile( '[%s]' % re.escape( string.punctuation ) )
	keyword_dict = {}
	for center in selected_articles:
		cluster = cluster_articles[center]
	#for center, cluster in cluster_articles:
		all_cluster_title_words = []
		for article in cluster:	
			all_cluster_title_words.extend([word for word in punc.sub('',article.title).split(" ") if word not in stop_words])
			# for word in punc.sub('',).split(" "):
			# 	if word not in stop_words:
			# 		all_words.append(word)
		a = sorted([[len([b for b in all_cluster_title_words if b == word]),word] for word in list(set(all_cluster_title_words))],reverse=True)
		keyword_dict[center] = a[0][1]
		#}keywords.append(a[0][1].title())

	return keyword_dict
