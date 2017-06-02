from django.test import TestCase
from scope.methods.dataprovider.news_handler import ScopeNewspaperArticle
from scope.methods.dataprovider.blacklist import Blacklist
from scope.methods.dataprovider import imap_handler, er_handler, news_handler, url_extractor

import spacy

from scope.models import Newsletter
from scope.methods.dataprovider.news_handler import NewsSourceHandler

import scope.methods.tests.testutils as testutils

class Provider_Object_Tests(TestCase):
	def test_out_type_save_articles(self):
		pass



	# def test_save_articles_with_imap_not_redundant(self):
	# 	agent = Agent

class Extractor_Tests(TestCase):
	def test_extraction(self):
			nlp = spacy.load("de")
			extractor = url_extractor.Extractor(nlp)

			urls = (
			    "http://hyperallergic.com/343745/"
			    "the-passionate-art-of-lgbtq-prisoners-in-the-us/"
			    " "
			    "http://www.androidheadlines.com/2016/12/"
			    "verizon-carry-blackberry-mercury-bbb100-us.html"
			    " "
			    "http://www.usnews.com/news/business/articles/2016-12-27/"
			    "troubled-italian-bank-says-capital-hole-bigger-than-expected"
			    " "
			    "http://www.androidheadlines.com/2016/12/"
			    "verizon-carry-blackberry-mercury-bbb100-us.html"
			    " "
			    "http://www.usnews.com/news/stem-solutions/articles/"
			    "2016-11-28/wi-fi-microscopes-help-corpus-christi-students-with-science"
			    " "
			    "https://twitter.com/SteveMartinToGo/status/813826846722760705"
			    " "
			    )

			self.assertEqual(len(extractor.get_urls_from_string(urls)), 5)

class ImapHandler_Tests(TestCase):
	def test_merge_mails_from_same_newsletter(self):
		agent, language = testutils.create_agent_and_language("commerzbank_germany")
		ih = imap_handler.ImapHandler(agent,language)
	#running this test with an article_dict, since it doesn't really make a difference for that method
		l = testutils.create_article_dict(10, 20)
		l = [l[0],l[1],l[0]]
		out = ih._merge_mails_from_same_newsletter(l)
		self.assertEqual(len(out),2)
		self.assertEqual(list(set(out[0][0])),out[0][0])
		self.assertIsInstance(out,list)
		self.assertIsInstance(out[0][1], Newsletter)

class NewsHandler_Tests(TestCase):
	def test_type_produce_output_dict(self):
		l = testutils.create_article_dict(50,30)
		news = NewsSourceHandler()
		out = news.produce_output_dict(l)
		self.assertIsInstance(out,list)
		self.assertIsInstance(out[0],dict)
		self.assertTrue('body' in out[0])

class Blacklist_Tests(TestCase):
	def test_blacklist_object_(self):
		good_article = ScopeNewspaperArticle(url="https://www.washingtonpost.com/news/powerpost/paloma/the-health-202/2017/05/25/the-health-202-the-cbo-report-is-bad-news-for-republicans-on-health-care/5925e34ce9b69b2fb981db8d/?utm_term=.506fc8d7b3ef")
		bad_url = ScopeNewspaperArticle(url="www.w3.org")
		bad_title = ScopeNewspaperArticle(url='http://www.samplewords.com/job-application-form/')
		bad_text = ScopeNewspaperArticle(url='http://usa.aopen.com')
		l = [good_article,bad_url,bad_title,bad_text]
		for item in l:
			item.download()
			item.parse()
		blacklist = Blacklist()
		out = blacklist.filter(l)
		self.assertEqual(len(out),1)
