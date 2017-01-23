import django
django.setup()

import pandas as pd

from scope.models import Article


articles = Article.objects.all()

raw = [[0, t.title, t.body.replace("\n", "")] for t in articles]

out = pd.DataFrame(raw, columns=["is_tech", "title", "text"])

out.to_csv("train.csv", index=False, encoding="utf-8")
