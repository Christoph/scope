import json
import constants


class Crawler(object):
    """docstring for crawler."""
    def __init__(self, language):
        self.lang = language

    def load_JSON(self, querys):
        data = []

        for query in querys:
            # Load JSON
            raw = json.loads(open('last24h/static/commerz/er_' + query + '_' + self.lang + '.json').read())

            # Get data
            temp = [doc for doc in raw if (doc['title'] not in constants.EXCLUDE and constants.UNSUBSCRIBE_EXCLUDE not in doc['body'] and doc['isDuplicate'] is False)]

            # Add good news
            data.extend(temp)

            # Save test data
            # with open('last24h/static/commerz/er_test_ger.json', 'w+') as outfile:
            #    json.dump(data[0:20], outfile, sort_keys=True, indent=4)
        return data
