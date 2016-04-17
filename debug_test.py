from last24h.tasks import cs_work

feeds = ['https://news.google.co.uk/news/feeds?pz=1&cf=all&ned=en&hl=en&q=Trump&output=rss&num=100']

strin = 'helloo'

cs_work.delay(feeds, strin)

