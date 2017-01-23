import django
django.setup()

import numpy as np
import pandas as pd
import json
import spacy
from django.core import serializers

from scope.models import Article
from scope.methods.learning import binary_classifier

pipeline = spacy.load("en")

# GET DATA FROM JSON
with open('research/clustering/articles.json', 'r') as stream:
    data = json.load(stream)

db_articles = []
for obj in serializers.deserialize("json", data):
    db_articles.append(obj.object)

db_articles = np.array(db_articles)

# Load classifier
classifier = binary_classifier.nh_classifier(pipeline)

# Classify articles
classified_aricles = classifier.classify(db_articles)

# Test performance
