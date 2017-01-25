
import csv, sys
from datetime import date, timedelta

from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer, Curate_Customer_Selection
from scope.models import Customer

reload(sys)
sys.setdefaultencoding('utf8')

#exporting to csv
def write_csv(article_list, filename):
	# open a file for writing.
	csv_out= open(filename + ".csv", 'wb')

	# create the csv writer object.
	mywriter = csv.writer(csv_out)

	# writerow - one row of data at a time.
	for item in article_list:
	    mywriter.writerow(item.body)

	# always make sure that you close the file.
	# otherwise you might find that it is empty.
	csv_out.close()


#####To extract the training data:

def find_selected_articles(customer_key, range, name, type):
	customer = Customer.objects.get(customer_key=customer_key)
	curate_customer = Curate_Customer.objects.get(customer=customer)

#relevant query date range (this is necessary here, because I've played with the interface in the begining and haven't yet cleaned up)
	time = date.today() - timedelta(days= range)
	queries = Curate_Query.objects.filter(time_stamp__gt = time).filter(curate_customer=curate_customer)

	if type=='name':
		selection_options = Curate_Customer_Selection.objects.filter(curate_customer=curate_customer).filter(name=name).all()
	elif type=='type':
	#or go via selection type "mistake" or "selection"
		selection_options = Curate_Customer_Selection.objects.filter(curate_customer=curate_customer).filter(type=name).all()
	suggestions = []
	for i in Article_Curate_Query.objects.filter(curate_query__in =queries).all():
	            for option in selection_options:
	                if option in i.selection_options.all():
	                    suggestions.append(i.article)

	return suggestions


def export_to_csv(customer_key, range, name, type):
	article_list = find_selected_articles(customer_key, range, name, type)
	write_csv(article_list,name + '_' + customer_key + '_' + date.today().isoformat())


#######to add new training data:

### in curate/views.py in @interface in line 32-34 (although yo woudl of course load the classifier on line 24 or so.)
def add_to_classifier(curate_selection_option, article_curate_instance,curate_customer):
	classifier = load_classifier(curate_customer)
	add_to_classifier(text=article_curate_instance.article.body, label=curate_selection_option.name)

