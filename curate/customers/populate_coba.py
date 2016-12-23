from scope.models import Customer, Agent, AgentImap
from curate.models import Curate_Customer
import datetime

# Create IMAP object
imap = AgentImap.objects.get_or_create(
    user="cobanewsletter",
    pwd="cobawilllesen",
    imap="imap.gmail.com",
    mailbox="[Gmail]/All Mail")[0]

imap.save()

# Create Customer
customer = Customer.objects.get_or_create(
    name="CoBaTest", customer_key="coba", email="test@scope.ai")[0]

# Create Curate_Customer
curate_customer = Curate_Customer.objects.get_or_create(
    customer=customer,
    key="key",
    defaults={"expires": datetime.date.today()+datetime.timedelta(days=365)}
    )[0]

# Create Source for the Curate_Customer
agent = Agent(
    product_customer_object=curate_customer,
    agent_object=imap
)

agent.save()
