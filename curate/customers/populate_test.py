from scope.models import Article, Customer, Source, AgentImap
from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer
import datetime

# Create IMAP object
imap = AgentImap(user="renesnewsletter", pwd="renewilllesen",
    imap="imap.gmail.com", mailbox="[Gmail]/All Mail")

imap.save()

# Create Customer
customer = Customer(
    name="Neuland Herzer Test", customer_key="key", email="test@test.com")

customer.save()

# Create Curate_Customer
curate_customer = Curate_Customer(
    customer=customer,
    key="key",
    expires=datetime.date.today() + datetime.timedelta(days=365))

curate_customer.save()

# Create Source for the Curate_Customer
source = Source(
    product_customer_object=curate_customer,
    agent_object=imap
)

source.save()
