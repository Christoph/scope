from scope.methods.dataprovider import constants


class Blacklist(object):
#accepts Newspaper package Articles, NOT DB Article objects, (although that could easily be fixed)
	def __init__(self):
		pass

	def filter(self, articles):
		out = []
		for article in articles:
			if self._title_check(article.title) and self._text_check(article.text) and self._url_check(article.url):
				out.append(article)
			else:
				print "Filtered by blacklists"
				print article.title
		return out

	def _title_check(self, title):
		if title not in constants.EXCLUDE and not self._blacklist_comparison(constants.TITLE_BLACKLIST, title):
			return True
		else: 
			return False

	def _text_check(self, text):
		if len(text)> 0 and not self._blacklist_comparison(constants.TEXT_BLACKLIST, text):
			return True
		else: 
			return False

	def _url_check(self, url):
		if not self._blacklist_comparison(constants.URL_HOSTNAME_BLACKLIST, url):
			return True
		else: 
			return False

	def _blacklist_comparison(self, blacklist, text):
		return any([item in text for item in blacklist])
