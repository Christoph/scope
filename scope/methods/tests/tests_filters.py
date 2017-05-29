from django.test import TestCase
from scope.methods.filters import *
from scope.models import Newsletter

import scope.methods.tests.testutils as testutils

class Scope_Filter_Tests(TestCase):

	def test_remove_duplicate_from_same_newsletter(self):
		l = testutils.create_article_dict(50,30)
		out = remove_duplicate_articles_from_same_newsletter(l)
		self.assertEqual(len(out[0][0]),50)
		self.assertIs(out[0][1],l[0][1])
		self.assertEqual(len(out[1][0]),30)
		self.assertIs(out[1][1],l[1][1])
		