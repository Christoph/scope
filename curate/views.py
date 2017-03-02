from django.shortcuts import render, redirect
from datetime import datetime
import ConfigParser

from conf.settings.importer import ImportGlobal
from curate.tasks import send_newsletter_task, selection_made_task
from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer, Curate_Customer_Selection
from scope.models import Customer, UserProfile

im = ImportGlobal()

def interface(request,customer_key, date_stamp=None):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if not customer_key == user_profile.customer.customer_key:
            return redirect('/login/?next=%s' % request.path)
    except:
        return redirect('/login/?next=%s' % request.path)


    customer = Customer.objects.get(customer_key=customer_key) #will be replaced by authentication
    curate_customer = Curate_Customer.objects.get(customer=customer)
    if date_stamp==None:
            query = Curate_Query.objects.filter(curate_customer=curate_customer).order_by("pk").last()
    else:
        date_parsed = datetime.strptime(date_stamp,'%d%m%Y').date()
        query = Curate_Query.objects.filter(curate_customer=curate_customer).filter(time_stamp=date_parsed).order_by("pk").last()
    suggestions = Article_Curate_Query.objects.filter(curate_query=query).filter(rank__gt = 0).order_by("rank")
    options = Curate_Customer_Selection.objects.filter(curate_customer=curate_customer).order_by("pk")
    if request.method == 'POST':
        config = ConfigParser.RawConfigParser()
        config.read('curate/customers/' + customer_key +
                         "/" + customer_key + '.cfg')
        query.selection_made = True
        query.save()
        selected_articles = []
        for i in range(1, len(suggestions) + 1):
            for option in options:                    
                try:
                    xx = request.POST[option.name + str(i)]
                    if xx == 'on':
                        s = suggestions[i-1]
                        selected_articles.append({"title": s.article.title, "body": s.article.body[0:200], "selection": option.name})
                        for reason in option.rejection_reason.all():
                            try:
                                yy = request.POST[option.name + str(i) + reason.name]
                                print yy
                                if  yy == "on":
                                    if reason.kind == "sou":
                                        curate_customer.bad_source.add(s.article.source)
                                        curate_customer.save()
                                    else:
                                        reason.current_members.add(s)
                                        reason.save()
                                        if reason.kind == "con":
                                            s.bad_article = True
                            except:
                                pass
                        s.selection_options.add(option)
                        s.save()
                except:
                    pass
                    
        try:
            selection_made_task(customer_key, selected_articles)
            selection_made_task.delay(customer_key, selected_articles)
        except:
            pass
        try:
            print im.get_env_variable('DJANGO_SETTINGS_MODULE')
            print config.getboolean('meta','direct_outlet')
            if config.getboolean('meta','direct_outlet') and im.get_env_variable('DJANGO_SETTINGS_MODULE') == "conf.settings.deployment":
                send_newsletter_task.delay(customer_key)
        except:
            pass

    stats = {}
    for option in options.all():
        stat = [i for i in suggestions if option in i.selection_options.all()]
        stats[option] = len(stat)
    context = {"stats": stats, "suggestions": suggestions, "options": options, 'query': query, 'customer_key': customer_key}
    return render(request, 'curate/interface.html', context)

def mail(request, customer_key):
    customer = Customer.objects.get(customer_key=customer_key)
    curate_customer = Curate_Customer.objects.get(customer=customer)
    query = Curate_Query.objects.filter(
        curate_customer=curate_customer).order_by("pk").last()
    config = ConfigParser.RawConfigParser()
    config.read('curate/customers/' + customer_key +
                "/" + customer_key + '.cfg')

    # recipients = config.get('outlet', 'recipients').split(',\n')
    # template_no = config.getint('outlet', 'mail_template_no')

    if config.get('outlet', 'options') == 'all':
        selection_options = Curate_Customer_Selection.objects.filter(
            curate_customer=curate_customer).filter(kind="sel").all()
    else:
        names = config.get('outlet', 'options').split(',')
        selection_options = Curate_Customer_Selection.objects.filter(
            curate_customer=curate_customer).filter(name__in=names).all()
    articles = []
    for option in selection_options:
        articles.extend([i.article for i in Article_Curate_Query.objects.filter(curate_query=query).filter(
            selection_options= option).order_by("rank").all()])
    stats_dict = {'name': config.get('meta', 'name'), 'words': query.processed_words,
                  'no_of_articles': query.articles_before_filtering}
    context = {"articles": articles, "stats_dict": stats_dict}
    return render(request, 'curate/mail_template.html', context)
