from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import numpy as np
import spacy
from collections import defaultdict
from scipy.stats import entropy

from scope.methods.semantics import preprocess

class Mutual_Information(object):
#accepts Newspaper package Articles, NOT DB Article objects, (although that could easily be fixed)
	def __init__(self, input_docs):
		self.input_docs = input_docs

	def preprocess(self, lang):
		self.nlp = spacy.load(lang)
		self.preprocessor = preprocess.PreProcessing(lang=lang, nlp=self.nlp)
		self.input_docs = self.preprocessor.noun_based_preprocessing(self.input_docs)

	def ngram_based(self, lower, upper):
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

	def mutual(self, previous, y):
		total = set(range(len(self.input_docs)))
		first = self._conditional_ent(y, previous)
		second = self._conditional_ent(y, total - (previous | y))
		return first - second


	def find_max(self, k):
		#start with empty set
		total = set(range(len(self.input_docs)))
		selection = []
		while len(selection) < k:
			s = set(selection)
			best_inf = [0,0]
			for i in (total - s):
				new_inf = self.mutual(s,{i}) 
				if new_inf > best_inf[1]:
					best_inf = [i,new_inf]
			selection.append(best_inf[0])

		total_prob = self._get_prob(total)
		total_ent = entropy(total_prob)
		selection_prob = self._get_prob(set(selection))
		selection_ent = entropy(selection_prob)
		ratio = selection_ent/total_ent

		return selection, ratio

	def ngram_selection(self, k,lower,upper, lang):
		self.preprocess(lang)
		self.ngram_based(lower, upper)
		selection, ratio = self.find_max(k)

		return selection, ratio

			