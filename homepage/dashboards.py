from controlcenter import Dashboard, widgets, app_settings
from scope.models import Newsletter, Source
from curate.models import Curate_Query, Curate_Query_Cluster, Article_Curate_Query
from curate.convenience.functions import retrieve_objects

from django.db.models import Avg, Count, Case, When
from math import *
from email.header import decode_header
from django.core.urlresolvers import reverse
import base64


def get_query(widget):
	customer_key = widget.init_options['customer_key']
	customer, curate_customer, queries, articles = retrieve_objects(
		customer_key, range=1)
	query_id = int(widget.request.GET.get('q', 0))
	if query_id == 0:
		query = Curate_Query.objects.get(pk=queries[0].pk)
	else:
		query = Curate_Query.objects.get(pk=int(query_id))
	return query

def get_curate_customer(widget):
	customer_key = widget.init_options['customer_key']
	customer, curate_customer = retrieve_objects(
		customer_key)
	return curate_customer


######### Widgets for overall Dashboard

# class TotalSummaryWidget(widgets.ItemList):
# 	title = "Total Summary"

# 	def get_queryset(self):
# 		curate_customer = get_curate_customer(self)
# 		queryset = curate_customer
# 	# def get_queryset(self):
# 	# 	query = get_query(self.request, "commerzbank_germany")
# 	# 	return 	Curate_Query.objects.filter(pk=query.pk)

# 	def produce_summary(self, obj):
# 		total_processed_words = ""
# 		number_of_inputs = ""

# 		return '<strong>Created:</strong> ' + str(obj.time_stamp.isoformat()) + '</br><strong>Processed Words:</strong> ' + str(obj.processed_words) + '</br><strong>Incoming Articles:</strong> ' + str(obj.articles_before_filtering) + '</br><strong>Selection Made: </strong>' + str(obj.selection_made)
# 	produce_summary.short_description = ""
# 	produce_summary.allow_tags = True

# 	def creation_date(self, obj):
# 		return ''#obj.time_stamp.isoformat()
# 	creation_date.short_description = "Created"

# 	template_name = 'single_query_overview.html'
# 	template_name_prefix = 'controlcenter/widgets/'
# 	width = 3
# 	height = 120
# 	list_display = ('creation_date', 'produce_summary')




class IncomingArticlesWeekdayWidget(widgets.LineChart):
	title = "Incoming articles per weekday"

	class Chartist:
		options = {
            'reverseData': False,
        }

	def labels(self):
		return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']

	def series(self):
		curate_customer = get_curate_customer(self)
		query = Curate_Query.objects.filter(curate_customer=curate_customer).order_by('-processed_words')
		l = []
		for i in range(2, 7):
			if query.filter(time_stamp__week_day=i).aggregate(avg=Avg('articles_before_filtering'))['avg'] != None:
				l.append(int(query.filter(time_stamp__week_day=i).aggregate(
					avg=Avg('articles_before_filtering'))['avg']))
		return [l]


class IncomingArticlesWidget(widgets.LineChart):
	title = "# of incoming articles"
	width = widgets.LARGE

	class Chartist:
		options = {
			'fullWidth': True,
			'fullHeight': True,
		}


	def get_queryset(self):
		curate_customer = get_curate_customer(self)
		queries = Curate_Query.objects.filter(
		curate_customer=curate_customer).order_by('-time_stamp')
		return queries

	def labels(self):
		l = []
		count = 1
		
		queries = self.get_queryset()
		# Curate_Query.objects.filter(
		# curate_customer=curate_customer).order_by('-time_stamp')
		for query in queries:
			if count % 7 == 1:
				l.append(query.time_stamp.isoformat())
			else:
				l.append('')
			count += 1
		return l

	def series(self):
		k = []
		# curate_customer = get_curate_customer(self)
		queries = self.get_queryset()
		# Curate_Query.objects.filter(
		# curate_customer=curate_customer).order_by('-time_stamp')
		for query in queries:
			if query.articles_before_filtering == None:
				var = 0
			else:
				var = int(query.articles_before_filtering)
			k.append(var)
		return [k]


class FavoriteSourcesWidget(widgets.ItemList):
	title = "Most selected Sources"
	def get_queryset(self):
		curate_customer = get_curate_customer(self)
		# customer_key = self.init_options['customer_key']
		# customer, curate_customer = retrieve_objects(customer_key)
		queryset = Source.objects.all().annotate(count=Count(Case(When(article__article_curate_query__curate_query__curate_customer=curate_customer,
																   article__article_curate_query__rank__gt=0, then=1)))).order_by('-count')
		return queryset


	def decoded_name(self, obj):
		return decode_header(obj.name)[0][0]

	decoded_name.short_description = "Name"
	width = widgets.LARGE
	height = 1300
	sortable = True
	list_display = (app_settings.SHARP, 'decoded_name', 'count')


class FavoriteNewslettersWidget(widgets.ItemList):
	title = "Most selected Newsletters"
	def get_queryset(self):
		customer_key = self.init_options['customer_key']
		customer, curate_customer = retrieve_objects(customer_key)
		queryset = Newsletter.objects.all().annotate(count=Count(Case(When(article_curate_query__curate_query__curate_customer=curate_customer,
																	   article_curate_query__rank__gt=0, then=1)))).order_by('-count')
		return queryset

	def decoded_name(self, obj):
		return decode_header(obj.name)[0][0]

	decoded_name.short_description = "Name"
	sortable = True
	list_display = (app_settings.SHARP, 'decoded_name', 'count')


class WorstNewslettersWidget(widgets.ItemList):
	title = "Newsletters with most bad articles"
	def get_queryset(self):
		customer_key = self.init_options['customer_key']
		customer, curate_customer = retrieve_objects(customer_key)
		queryset = Newsletter.objects.all().annotate(count=Count(Case(When(article_curate_query__curate_query__curate_customer=curate_customer,
																	   article_curate_query__bad_article=True, then=1)))).order_by('-count')
		return queryset

	def decoded_name(self, obj):
		return decode_header(obj.name)[0][0]

	decoded_name.short_description = "Newsletter"
	sortable = True
	list_display = (app_settings.SHARP, 'decoded_name', 'count')


class WorstSourcesWidget(widgets.ItemList):
	title = "Sources with most bad articles"
	def get_queryset(self):
		customer_key = self.init_options['customer_key']
		customer, curate_customer = retrieve_objects(customer_key)
		queryset = Source.objects.all().annotate(count=Count(Case(When(article__article_curate_query__curate_query__curate_customer=curate_customer,
																   article__article_curate_query__bad_article=True, then=1)))).order_by('-count')
		return queryset

	def decoded_name(self, obj):
		return decode_header(obj.name)[0][0]

	decoded_name.short_description = "Source"
	sortable = True
	list_display = (app_settings.SHARP, 'decoded_name', 'count')


class BadArticlesWidget(widgets.ItemList):
	title = "Recent Bad Articles"
	def get_queryset(self):
		customer_key = self.init_options['customer_key']
		customer, curate_customer = retrieve_objects(customer_key)
		queryset = Article_Curate_Query.objects.filter(
		curate_query__curate_customer=curate_customer, bad_article=True).order_by('curate_query__time_stamp')
		return queryset

	def get_title(self, obj):
		return obj.article.title
	get_title.short_description = "Bad Article"

	def get_source(self, obj):
		return decode_header(obj.article.source.name)[0][0]
	get_source.short_description = "Source"

	def get_newsletter(self, obj):
		return decode_header(obj.newsletter.name)[0][0]
	get_newsletter.short_description = "Newsletter"

	list_display = ('get_title', 'get_source', 'get_newsletter')



############ WIdgets for query specific Dashboard

class SingleQueryWidget(widgets.ItemList):
	title = "Summary"
	# customer_key = self.init_options['customer_key']
	def get_queryset(self):
		query = get_query(self)
		return 	Curate_Query.objects.filter(pk=query.pk)

	def produce_summary(self, obj):
		return  '<strong>Created:</strong> ' + str(obj.time_stamp.isoformat()) + '</br><strong>Processed Words:</strong> ' + str(obj.processed_words) + '</br><strong>Incoming Articles:</strong> ' + str(obj.articles_before_filtering) + '</br><strong>Selection Made: </strong>' + str(obj.selection_made)
	produce_summary.short_description = ""
	produce_summary.allow_tags = True

	def creation_date(self, obj):
		return ''#obj.time_stamp.isoformat()
	creation_date.short_description = "Created"

	template_name = 'single_query_overview.html'
	template_name_prefix = 'controlcenter/widgets/'
	width = 3
	height = 120
	list_display = ('creation_date', 'produce_summary')


class MovetoOtherClustersWidget(widgets.ItemList):
	title = "Jump to Query"
	def get_queryset(self):
		customer_key = self.init_options['customer_key']
		customer, curate_customer = retrieve_objects(customer_key)
		queryset = Curate_Query.objects.filter(
			curate_customer=curate_customer).order_by('-pk')
		return queryset

	def get_link_to_dashboard(self, obj):
		link = reverse('controlcenter:dashboard', kwargs={
					   'pk': 0}) + '?q=' + str(obj.pk)
		return '<a href=' + link + '>' + obj.time_stamp.isoformat() + '</a>'

	get_link_to_dashboard.short_description = "Query"
	get_link_to_dashboard.allow_tags = True
	list_display_links = ('selection_made')
	sortable = True
	limit_to = 500
	height = 120
	width = 2
	list_display = ('get_link_to_dashboard', 'selection_made')


class SelectedArticlesQueryWidget(widgets.ItemList):
	# selected articles, bad articles
	title = "Selected articles"
	def get_queryset(self):
		query = get_query(self)
		return query.selected_articles()

	def get_title(self, obj):
		return obj.article.title
	get_title.short_description = "Selection"

	def get_source(self, obj):
		if obj.article.source != None:
			return decode_header(obj.article.source.name)[0][0]
		else: 
			return ""
	get_source.short_description = "Source"

	def get_newsletter(self, obj):
		if obj.newsletter != None:
			return decode_header(obj.newsletter.name)[0][0]
		else: 
			return ""
	get_newsletter.short_description = "Newsletter"

	list_display = ('get_title', 'get_source', 'get_newsletter')

class BadArticlesQueryWidget(widgets.ItemList):
	# selected articles, bad articles
	title = "Bad articles"
	def get_queryset(self):
		query = get_query(self)
		return query.bad_articles()

	def get_title(self, obj):
		return obj.article.title
	get_title.short_description = "Bad Article"

	def get_source(self, obj):
		if obj.article.source != None:
			return decode_header(obj.article.source.name)[0][0]
		else: 
			return ""
	get_source.short_description = "Source"

	def get_newsletter(self, obj):
		if obj.newsletter != None:
			return decode_header(obj.newsletter.name)[0][0]
		else: 
			return ""
	get_newsletter.short_description = "Newsletter"

	list_display = ('get_title', 'get_source', 'get_newsletter')


class QueryChartWidget(widgets.SingleBarChart):
	#display the distribution of cluster sizes 
	title = "Distribution of Cluster sizes"
	def get_queryset(self):
		query = get_query(self)
		queryset = Curate_Query_Cluster.objects.filter(
				center__curate_query=query).order_by('pk').annotate(count=Count('cluster_articles')).order_by('rank')
		return queryset

	# def labels(self):
	# 	pass

	# def get_rank(self,obj):
	# 	return obj.center.rank

	limit_to = 15
	values_list = ('rank', 'count')


class ClusterandNewsletterWidget(widgets.BarChart):
	#display the distribution of cluster sizes 
	title = "By Newsletter"

	class Chartist:
		options = {
		'stackBars': True,
		# 'seriesBarDistance': 10,
			'fullWidth': True,
			'fullHeight': True,
		}

	def get_queryset(self):
		query = get_query(self)
		queryset = Curate_Query_Cluster.objects.filter(
				center__curate_query=query).order_by('pk').annotate(count=Count('cluster_articles')).order_by('rank')
		return queryset

	def legend(self):
		query = get_query(self)
		newsletters = Newsletter.objects.filter(article_curate_query__curate_query=query).distinct()
		return [decode_header(newsletter.name)[0][0] for newsletter in newsletters]

	def labels(self):
		return [str(cluster.rank) for cluster in self.get_queryset()]

	def series(self):
		query = get_query(self)
		newsletters = Newsletter.objects.filter(article_curate_query__curate_query=query).distinct()
		ser = []
		for newsletter in newsletters:
			series_for_newsletter = []
			for cluster in self.get_queryset():
				series_for_newsletter.append(cluster.cluster_articles.all().filter(newsletter=newsletter).count())
			if sum(series_for_newsletter) >0:
				ser.append(series_for_newsletter)
		return ser		


class ClusterandSourcesWidget(widgets.BarChart):
	#display the distribution of cluster sizes 
	title = "By Source"

	class Chartist:
		options = {
		'stackBars': True,
		# 'seriesBarDistance': 10,
			'fullWidth': True,
			'fullHeight': True,
		}

	def get_queryset(self):
		query = get_query(self)
		queryset = Curate_Query_Cluster.objects.filter(
				center__curate_query=query).order_by('pk').annotate(count=Count('cluster_articles')).order_by('rank')
		return queryset

	def legend(self):
		query = get_query(self)
		sources = Source.objects.filter(article__article_curate_query__curate_query=query).distinct()
		return [decode_header(source.name)[0][0] for source in sources]

	def labels(self):
		return [str(cluster.rank) for cluster in self.get_queryset()]

	def series(self):
		query = get_query(self)
		sources = Source.objects.filter(article__article_curate_query__curate_query=query).distinct()
		ser = []
		for source in sources:
			series_for_source = []
			for cluster in self.get_queryset():
				series_for_source.append(cluster.cluster_articles.all().filter(article__source=source).count())
			if sum(series_for_source) >0:
				ser.append(series_for_source)
		return ser	
	# def get_no_of_newsletters(self,obj):

	# 	return obj.center.rank

	# limit_to = 15
	# values_list = ('rank', 'count')



class ClustersWidget(widgets.ItemList):
	title = "Clusters Details "
	def get_queryset(self):
		query = get_query(self)
		queryset = Curate_Query_Cluster.objects.filter(
				center__curate_query=query).select_related('center').prefetch_related('cluster_articles').order_by('pk')
		return queryset

	def get_central_title(self, obj):
		return obj.center.article.title
	get_central_title.short_description = "Central article"
	def get_central_source(self, obj):
		return obj.center.article.source.name
	get_central_source.short_description = "Source of central article"

	def get_central_newsletter(self, obj):
		return decode_header(obj.center.newsletter.name)[0][0]
	get_central_newsletter.short_description = "Newsletter of central article"


	# def get_cluster_articles(self, obj):
	# 	info = obj.cluster_articles.all().values(
	# 		'article__title', 'article__source__name', 'newsletter__name')
	# 	s = ''
	# 	for item in info:
	# 		decoded_name = decode_header(item['newsletter__name'])[0][0]
	# 		if isinstance(decoded_name, bytes):
	# 			newsletter_name = decoded_name.decode('utf-8')
	# 		elif isinstance(decoded_name, str):
	# 			newsletter_name = decoded_name
	# 		else: 
	# 			newsletter_name = "N/A"
	# 		#base64.b64decode(decode_header(item['newsletter__name'])[0][0])
	# 			# s.append([item['article__title'],item['article__source__name']])
	# 		s = s + '<strong>Title</strong>: ' + item['article__title'] + ', <strong>Source</strong>: ' + item[
	# 		'article__source__name'] + ', <strong>Newsletter</strong>: ' + newsletter_name + '<br/>'
	# 	return s

	# get_cluster_articles.allow_tags = True
	# get_cluster_articles.short_description = "Cluster Articles"

	sortable = True
	list_display = ('rank', 'get_central_title',
					"get_central_source", 'get_central_newsletter', 'keywords')#'summary')#,'get_cluster_articles')
	limit_to = 15
	width = 3


############# Dashboards


# dashboard to evaluate a single curate_query
class Curate_Query_Dashboard(Dashboard):
	title = "Single Edition Overview"
	widgets = (
		ClustersWidget, 
		(SingleQueryWidget,MovetoOtherClustersWidget),
		widgets.Group([QueryChartWidget, ClusterandNewsletterWidget, ClusterandSourcesWidget], width=3),
		
			
		# (SingleQueryWidget,MovetoOtherClustersWidget)
		

		# widgets.Group([,MovetoOtherClustersWidget], width=2),
		widgets.Group([SelectedArticlesQueryWidget,BadArticlesQueryWidget], width=3),
	)

# dashboard to evaluate a customer's overall curate history


class Curate_History_Dashboard(Dashboard):
	title = "Total History Overview"
	widgets = (
		(FavoriteSourcesWidget, FavoriteNewslettersWidget),
		(IncomingArticlesWidget, IncomingArticlesWeekdayWidget),
		widgets.Group([BadArticlesWidget, WorstNewslettersWidget, WorstSourcesWidget],
					  width=widgets.LARGE)
		# , FavoriteNewslettersWidget),

	)
