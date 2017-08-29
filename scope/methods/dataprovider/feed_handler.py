from scope.models import RSSFeed
from scope.methods.dataprovider import news_handler
from urllib.parse import urlparse
import feedparser

class Feed_Handler(object):
	def __init__(self):
		self.news = news_handler.NewsSourceHandler()

	def collect_used_feeds(self):
		used_feeds = RSSFeed.objects.filter(user_reader=user_reader).distinct()
		article_list = self._retrieve_from_feeds(used_feeds)
		return article_list

	def _retrieve_from_feeds(self, feeds):
		article_list = []
		for feed in feeds:
			d = feedparser.parse(feed.url)
			urls = [i.link for i in d.entries]	
			summaries = [self._get_summary(i) for i in d.entries]
			#timestamps = [self.get_timestamp(i) for i in d.entries]
			article_dict = self.news.get_articles_from_list([[urls,feed]])
			article_list.extend(self._produce_feed_output_dict(article_dict[0], summaries))
		return article_list

	def _get_summary(self,entry):
		if 'summary' in entry:
			aa = entry.summary
			if "<div>" in aa:
				try:
					aa = aa.split("<div>")[0] + " " + aa.split("<div>")[2]
				except:
					aa = aa.split("<div>")[0]
					
		return aa

	def _get_timestamp(self, entry):
		if 'published_parsed' in entry:
			ff = datetime.fromtimestamp(mktime(entry.published_parsed))
		else:
			ff = None
		return ff
	
	def _produce_feed_output_dict(self, article_dict, summaries):
		out = []
		for i in range(0,len(article_dict[0])):
			article = article_dict[0][i]
			out.append({
						"body": article.text, "title": article.title,
						"url": article.url, "images": article.top_image,
						"source": urlparse(article.url).netloc,
						"pubdate": article.publish_date,
						"summary": summaries[i],
						"feed": article_dict[1]})
		return out

