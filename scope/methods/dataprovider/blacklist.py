from scope.methods.dataprovider import constants


class Blacklist(object):
#accepts Newspaper package Articles, NOT DB Article objects, (although that could easily be fixed)
    def __init__(self):
    	pass
    	
    def filter(self, articles):
        out = []
        for article in self.articles:
            if article.title not in constants.EXCLUDE and not self._blacklist_comparison(constants.TITLE_BLACKLIST, article.title) and not self._blacklist_comparison(constants.TEXT_BLACKLIST, article.text) and len(article.text) > 0:
                out.append(article)
            else:
                print "Filtered by blacklists"
                print article.title
        return out

    def _blacklist_comparison(self, blacklist, text):
        for item in blacklist:
            if text.find(item) >= 0:
                return True
            else:
                return False
