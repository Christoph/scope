from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import numpy as np
import spacy
import csv
from collections import defaultdict
from scipy.stats import entropy

from scope.methods.semantics import preprocess
from scope.methods.graphs.clustering_methods import hc_create_linkage, hc_cluster_by_maxclust

class Mutual_Information(object):
#accepts Newspaper package Articles, NOT DB Article objects, (although that could easily be fixed)
	def __init__(self, input_docs):
		self.input_docs = input_docs
		self.titles = [i.title for i in input_docs]
		self.bodies = [i.body[0:400] for i in input_docs]
		self.total = set(range(len(self.input_docs)))

	def _preprocess(self, lang):
		self.nlp = spacy.load(lang)
		self.preprocessor = preprocess.PreProcessing(lang=lang, nlp=self.nlp)
		self.input_docs = self.preprocessor.noun_based_preprocessing(self.input_docs)
		

	def _ngram_based(self, lower, upper):
		self.idf = self._get_idf(lower, upper)
		self.count_matrix = self._get_count_matrix(lower, upper)

	def _get_idf(self, lower, upper):
		#produce idf vector
		bigram_vectorizer = TfidfVectorizer(ngram_range=(lower, upper),binary=True) 
		bigram_vectorizer.fit_transform(self.input_docs)
		idf = bigram_vectorizer.idf_
		return idf

	def _get_count_matrix(self, lower, upper):
		#produce occurrence table
		counter = CountVectorizer(ngram_range=(lower, upper)) 
		count_occurrences = counter.fit_transform(self.input_docs)
		matrix = count_occurrences.todense()
		return matrix

	def _get_prob(self, subset):
		# we Use this to calculate the total joint probability 
		#the approach here is to not go through the whole procedure of first generating the sparese global matrix and then tracing out, but rather as follows:
		#Given some set of document indices, we go through all the sus and generate a list of those combinations that occure, together with the indices of the sus in which they occur. 
		#Producing the entropy from this is easy. 

		sparse_dict = defaultdict()
		for unit in range(0,len(self.idf)):
			subset_count_for_unit = self.count_matrix[np.ix_(list(subset),[unit])]
			sparse_dict[unit] = subset_count_for_unit

		#now turn this around and generate the set of values for every subset_count
		new_dict = defaultdict(list)
		for k, v in sparse_dict.items():
			s = ''
			for i in v.tolist():
				s += chr(i[0])
			new_dict[s].append(k)

		partition_function = sum(self.idf)
		# in now forget about the actual counter_patterns and produce a vector only with the non-zero output weights
		output_vec = []
		for k, v in new_dict.items():
			weight = sum([self.idf[w] for w in v])
			output_vec.append(weight)
		return output_vec/partition_function

	def _conditional_ent(self, a, b):
		joint = self._get_prob(a.union(b))
		joint_ent = entropy(joint)

		single = self._get_prob(b)
		single_ent = entropy(single)

		return joint_ent - single_ent

	def _mutual_new(self, x, y):
		first = self._conditional_ent(y, x)
		second = self._conditional_ent(y, self.total - (x | y))
		return first - second

	def _mutual(self, x, y, normalized=False):
		singlex = self._get_prob(x)
		single_entx = entropy(singlex)
		singley = self._get_prob(y)
		single_enty = entropy(singley)
		joint = self._get_prob(x.union(y))
		joint_ent = entropy(joint)
		if normalized:
			return (single_entx + single_enty - joint_ent)/joint_ent
		else:
			return single_entx + single_enty - joint_ent

	def _find_max(self, k):
		#start with empty set
		selection = []
		while len(selection) < k:
			s = set(selection)
			best_inf = [0,0]
			for i in (self.total - s):
				new_inf = self._mutual_new(s,{i}) 
				if new_inf > best_inf[1]:
					best_inf = [i,new_inf]
			selection.append(best_inf[0])

		total_prob = self._get_prob(self.total)
		total_ent = entropy(total_prob)
		selection_prob = self._get_prob(set(selection))
		selection_ent = entropy(selection_prob)
		ratio = selection_ent/total_ent

		return selection, ratio

	def ngram_selection(self, k,lower,upper, lang):
		self._preprocess(lang)
		self._ngram_based(lower, upper)
		selection, ratio = self._find_max(k)

		return selection, ratio

	def get_learning_curve(self,selection_list):
		out = []
		total_prob = self._get_prob(self.total)
		total_ent = entropy(total_prob)
		for i in range(len(selection_list)):	
			selection_prob = self._get_prob(selection_list[:i])
			selection_ent = entropy(selection_prob)
			out.append(selection_ent/total_ent)
			
		return out

	def find_related_articles(self, y, no):
		s = []
		for i in (self.total - y):
			mutual = self._mutual(y,{i}) 
			s.append([i,mutual])
		return sorted(s, key= lambda el:el[1], reverse=True)[:no]


	def get_mi_list(self, normalized=False):
		out = []
		for i in range(len(self.total)):
			for j in range(i+1,len(self.total)):
				out.append([i,j,self._mutual({i},{j},normalized)])
		return out

	def create_hc(self):
		linkage_matrix = hc_create_linkage(vecs)
	    labels_hc = hc_cluster_by_maxclust(linkage_matrix, 0.6)
	    len_hc = len(np.unique(labels_hc))

	def produce_heatmap_info(self):
		#get matrix of mi for every pair
		l = self.get_mi_list()
		k = self.get_mi_list(normalized=True)
		#export tsv
		with open('static/research/mi/mi.tsv', 'w') as tsvfile:
		    writer = csv.writer(tsvfile, delimiter='\t', lineterminator='\n')
		    writer.writerow(["name_first", "name_second", "mi", "pk1", "pk2"])
		    for i in l:
		        writer.writerow([self.bodies[i[0]],self.bodies[i[1]],round(i[2],3), i[0],i[1]])
		    for i in k:
		        writer.writerow([self.bodies[i[1]],self.bodies[i[0]],round(i[2],3),i[1],i[0]])
		    for i in range(len(self.total)):
		    	writer.writerow([self.bodies[i],self.bodies[i],"1",i,i])


