import re
import string
from nltk.corpus import stopwords
from scope.methods.semantics import stopwords as stopw

def keywords_from_articles(list, lang):
	if lang == "en":
		stop_words = stopw.EN
	elif lang == "de":
		stop_words = stopwords.words('german')

	punc = re.compile( '[%s]' % re.escape( string.punctuation ) )
	keywords = []
	for item in list:
		all_words = []
		for word in punc.sub('',).split(" "):
			if word not in stop_words:
				all_words.append(word)
			a = sorted([[len([b for b in all_words if b == word]),word] for word in list(set(all_words))],reverse=True)
			keywords.append(a[0][1].title())

	return keywords
