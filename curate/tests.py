from django.test import TestCase
from curate.models import Article_Curate_Query, Curate_Customer, Curate_Query
from scope.models import Customer, Article, Source
from curate.methods import curate_process

from datetime import date

def create_test_customer(customer_key):
	customer = Customer(customer_key = customer_key)
	customer.save()
	curate_customer = Curate_Customer(customer=customer, expires = date.today())
	curate_customer.save()
	query = Curate_Query(curate_customer=curate_customer)
	query.save()
	return customer, curate_customer, query

class Curate_Object_Tests(TestCase):
	"""Checks the various methods of the Curate objects defined in curate_process.py"""

	def test_bad_articles_are_actually_filtered_test_by_title(self):
		customer, curate_customer, query = create_test_customer("commerzbank_germany")
		cur = curate_process.Curate(customer_key = "commerzbank_germany")
		article = Article(title="Test Title", url="url1") 
		article.save()
		article2 = Article(title="Test Title", url="url2") 
		article2.save()		
		bad_article = Article_Curate_Query(bad_article=True, article =article, curate_query=query)
		bad_article.save()

		self.assertIs(len(cur.filter_bad_articles([article2])), 0)
	
	def test_bad_articles_are_actually_filtered_test_by_url(self):
		customer, curate_customer, query = create_test_customer("commerzbank_germany")
		cur = curate_process.Curate(customer_key = "commerzbank_germany")
		article = Article(title="Test Title1", url="url") 
		article.save()
		article2 = Article(title="Test Title2", url="url") 
		article2.save()	
		bad_article = Article_Curate_Query(bad_article=True, article =article, curate_query=query)
		bad_article.save()

		self.assertIs(len(cur.filter_bad_articles([article2])), 0)
	
	def test_bad_sources_are_actually_filtered(self):
		customer, curate_customer, query = create_test_customer("commerzbank_germany")
		cur = curate_process.Curate(customer_key = "commerzbank_germany")
		source = Source(name="Bad Source")
		source.save()
		curate_customer.bad_source.add(source)
		curate_customer.save()
		article = Article(title="Test Title", url="url1", source=source) 
		article.save
		self.assertIs(len(cur.filter_bad_sources([article])), 0)
	

	def test_cluster_labels_are_stored_correctly(self):
		pass

	def test_the_right_number_of_clusters_are_produced(self):
		pass
