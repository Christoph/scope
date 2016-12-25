import sys
import ConfigParser

from curate.scripts import curate_process
import curate.methods.tests as tests
reload(sys)
sys.setdefaultencoding('utf8')

# customer_key = "neuland_herzer"
# model = "lsi"
# lower_step = 0
# upper_step = 0.5
# step_size = 0.01
# lower_bound = 6
# upper_bound = 20
# weight1 = 1
# weight2 = 0
# lsi_dim = 20


config = ConfigParser.RawConfigParser()
config.read('curate/customers/' + customer_key + '.cfg')

model = config.get('general','current_model')

test = tests.Curate_Test(config.get('general','current_test')).test

for test_params.append

weight1 = config.get('test','test_type')

test_params = [weight1, weight2]
params = [[lower_step, upper_step, step_size], test_params]
size_bound = [lower_bound, upper_bound]

curate = curate_process.Curate(
    model=model,
    customer_key=customer_key,
    test=test,
    params=params,
    size_bound=size_bound,
    lsi_dim=lsi_dim)

selected_articles = curate.from_sources()
print selected_articles
