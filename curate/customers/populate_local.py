from scope.models import Customer, AgentImap, Agent
from curate.models import Curate_Customer, Curate_Customer_Selection
import datetime

# Create IMAP object
imap = AgentImap.objects.get_or_create(user="renesnewsletter", pwd="renewilllesen",
    imap="imap.gmail.com", mailbox="[Gmail]/All Mail")[0]

# Create Customer
customer = Customer.objects.get_or_create(
    name="Neuland Herzer Test", customer_key="nh", email="test@test.com")[0]

# Create Curate_Customer
curate_customer = Curate_Customer.objects.get_or_create(
    customer=customer,
    key="key",
    defaults = {"expires": datetime.date.today() + datetime.timedelta(days=365)}
    )[0]

# Create Source for the Curate_Customer
agent = Agent(
    product_customer_object=curate_customer,
    agent_object=imap
)

agent.save()

selection = Curate_Customer_Selection(curate_customer=curate_customer, name="learn", type="mis", color="#e0340f")
selection.save()
selection = Curate_Customer_Selection(curate_customer=curate_customer, name="select", type="sel", color="#8ab6ee")
selection.save()
