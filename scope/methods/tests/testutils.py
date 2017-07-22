import configparser

from curate.models import Article_Curate_Query, Curate_Customer, Curate_Query
from scope.models import Customer, Article, Newsletter, AgentImap
from scope.methods.dataprovider.news_handler import ScopeNewspaperArticle

from math import *
from datetime import date
from random import randint

def create_agent_and_language(customer_key):
	config = configparser.RawConfigParser()
	config.read('curate/customers/' + customer_key +
					 "/" + customer_key + '.cfg')
	user = config.get('imap', 'user')
	pwd = config.get('imap', 'pwd')
	imap = config.get('imap', 'imap')
	mailbox = config.get('imap', 'mailbox')
	interval = config.get('imap', 'interval')
	language = config.get('general', 'language')
	agent = AgentImap(user=user,pwd=pwd,imap=imap,mailbox=mailbox,interval=interval)
	return agent, language

def create_newspaper_articles(no_articles):
	out = []
	count = 0
	for i in range(0, 3*no_articles):
		article = ScopeNewspaperArticle(title="Test Title" + str(count % no_articles),
						  url="https://url" + str(count % no_articles),
						  text= "some text " + str(i))
		out.append(article)
		count += 1
	return out

def create_article_dict(no_articles1, no_articles2):
	articles = create_newspaper_articles(no_articles1)
	articles2 = create_newspaper_articles(no_articles2)
	newsletter = Newsletter(name="Name", email="email@w.com")
	newsletter.save()
	newsletter2 = Newsletter(name="Name2",email="email2@w.com")
	newsletter2.save()
	l = [[articles,newsletter],[articles2,newsletter2]]
	return l

def create_test_customer(customer_key):
	customer = Customer(customer_key=customer_key)
	customer.save()
	curate_customer = Curate_Customer(customer=customer)
	curate_customer.save()
	query = Curate_Query(curate_customer=curate_customer)
	query.save()
	return customer, curate_customer, query

def create_labels(cluster_size, articles):
	pre_labels = list(zip(*[iter(articles)] * cluster_size))
	out = []
	for i in pre_labels:
		i = list(i)
		out.append([i[0], i])
	return out


def create_articles(no):
	out = []
	for i in range(0, no):
		article = Article(title="Test Title" + str(i),
						  url="https://url" + str(i))
		article.save()
		out.append(article)
	return out


def create_newsletters(no):
	out = []
	for i in range(0, no):
		item = Newsletter(name="Test Newsletter" + str(i),
						  email="paul@" + str(i) + ".com")
		item.save()
		out.append(item)
	return out


def create_instances(articles, query, newsletters):
	out = []
	for article in articles:
		newsletter = newsletters[randint(0, len(newsletters) - 1)]
		instance = Article_Curate_Query(
			article=article, curate_query=query, newsletter=newsletter)
		instance.save()
		out.append(instance)
	return out

