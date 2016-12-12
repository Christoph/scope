from scope.models import Customer, Agent, AgentImap
from curate.models import Curate_Customer
import datetime

# Create IMAP object
imap, create = AgentImap.objects.get_or_create(
    user="enews@neulandherzer.net",
    pwd="Ensemble_Enema",
    imap="imap.1und1.de",
    mailbox="INBOX")

imap.save()

# Create Customer
customer, create = Customer.objects.get_or_create(
    name="Neuland Herzer", customer_key="neuland_herzer", email="felix.fischer@neulandherzer.com")


# Create Curate_Customer
curate_customer, create = Curate_Customer.objects.get_or_create(
    customer=customer,
    key="key",
    defaults = {"expires": datetime.date.today() + datetime.timedelta(days=365)}
    )

# Create Source for the Curate_Customer
agent = Agent(
    product_customer_object=curate_customer,
    agent_object=imap
)

agent.save()
