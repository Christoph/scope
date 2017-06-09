from django.test import TestCase
from scope.models import Article
import scope.methods.semantics.keywords as keywordsfunc
import scope.methods.tests.testutils as testutils

class Keywords_Test(TestCase):
	def test_keywords_from_articles_produces_correct_types(self):
		customer, curate_customer, query = testutils.create_test_customer('test_customer')
		agent, language = testutils.create_agent_and_language("test_customer")
		articles = testutils.create_articles(30)
		cluster_articles = [[articles[0], articles[0:10]],[articles[11], articles[11:20]]]
		cluster_articles = dict(cluster_articles)
		selected_articles = [articles[0],articles[11]]
		keywords = keywordsfunc.keywords_from_articles(cluster_articles, selected_articles, language)
		self.assertIsInstance(keywords,dict)
		self.assertEqual(len(keywords),2)
		for key,value in keywords.items():
			self.assertIsInstance(key,Article)
			self.assertIsInstance(value,str)
		pass

