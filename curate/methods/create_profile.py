from django.contrib.auth.models import User
from scope.models import Customer, Agent, AgentImap, UserProfile
from curate.models import Curate_Customer, Curate_Customer_Selection
import datetime
import configparser


def create(name, email, selection_dict={}, imap_dict={"host": "gmail"}):
    proc_name = name.lower().replace(' ', '_')
    pwd = proc_name[0:3] + "willlesen"

    # Create IMAP object
    #
    print(pwd)
    if imap_dict['host'] == 'gmail':
        imap, created = AgentImap.objects.get_or_create(
            user=proc_name + '@gmail.com',
            pwd=pwd,
            imap="imap.gmail.com",
            mailbox="[Gmail]/All Mail")
    else:
        imap, created = AgentImap.objects.get_or_create(
            user=imap_dict['user'],
            pwd=imap_dict['pwd'],
            imap=imap_dict['imap_server'],
            mailbox=imap_dict['mailbox'],)
        pass

    imap.save()
    # Create User
    user, created = User.objects.get_or_create(username=proc_name)
    user.set_password(pwd)
    user.save()

    # Create Customer
    customer, created = Customer.objects.get_or_create(
        name=name, customer_key=proc_name, email=email)

    # Create UserProfile
    userprofile, created = UserProfile.objects.get_or_create(user=user, customer=customer, defaults={
        "activation_key": "activation_key", "expires": datetime.date.today() + datetime.timedelta(days=365)})

    # Create Curate_Customer
    curate_customer, created = Curate_Customer.objects.get_or_create(
        customer=customer,
        key="key",
        defaults={"expires": datetime.date.today(
        ) + datetime.timedelta(days=365)}
    )

    # Create Source for the Curate_Customer
    agent = Agent(
        product_customer_object=curate_customer,
        agent_object=imap
    )

    agent.save()

    for s in selection_dict:
        selection, created = Curate_Customer_Selection.objects.get_or_create(
            curate_customer=curate_customer, name=s.name, type=s.type, color=s.color)
        # selection.save()

    config = configparser.RawConfigParser()
    try:
        config.read('curate/customers/' + proc_name + '.cfg')

    except:
        pass

    try:
        config.add_section('meta')
        config.set('meta', 'name', name)
        config.set('meta', 'email', email)
    except:
        pass

    try:
        config.add_section('imap')
        config.set('imap', 'host', imap_dict['host'])
    except:
        pass

    # Writing our configuration file
    with open('curate/customers/' + proc_name + '.cfg', 'wb') as configfile:
        config.write(configfile)

    # Create selections"learn", "simple", "advanced"
