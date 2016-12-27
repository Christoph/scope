from scope.models import Customer, Agent, AgentImap
from curate.models import Curate_Customer, Curate_Customer_Selection
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
    name="Commerzbank Germany", customer_key="commerzbank_germany", email="michael.schneider2@commerzbank.com")[0]

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

# Create selections"learn", "simple", "advanced"
selection = Curate_Customer_Selection(curate_customer=curate_customer, name="learn", type="mis", color="#e0340f")
selection.save()
selection = Curate_Customer_Selection(curate_customer=curate_customer, name="simple", type="sel", color="#8ab6ee")
selection.save()
selection = Curate_Customer_Selection(curate_customer=curate_customer, name="advanced", type="sel", color="#4a2fec")
selection.save()
