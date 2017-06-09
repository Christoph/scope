from django.shortcuts import render, redirect
from datetime import datetime
import configparser
from django.contrib.auth.decorators import login_required

from conf.settings.importer import ImportGlobal
from curate.tasks import send_newsletter_task, selection_made_task
from scope.methods.semantics.keywords import keywords_from_articles
from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer, Curate_Customer_Selection, Curate_Query_Cluster
from scope.models import Customer, UserProfile


im = ImportGlobal()

@login_required()
def interface(request,customer_key=None, date_stamp=None):
    if customer_key != None:
        print(customer_key)
        if request.user.is_superuser:
            key = customer_key
        else:
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                if not customer_key == user_profile.customer.customer_key:
                    return redirect('/login/?next=%s' % request.path)
            except:
                return redirect('/login/?next=%s' % request.path)
    else:
        print("None")
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            key = user_profile.customer.customer_key
        except:
            return redirect('/login/?next=%s' % request.path)

    customer = Customer.objects.get(customer_key=key) #will be replaced by authentication
    curate_customer = Curate_Customer.objects.get(customer=customer)
    if date_stamp==None:
            query = Curate_Query.objects.filter(curate_customer=curate_customer).order_by("pk").last()
    else:
        date_parsed = datetime.strptime(date_stamp,'%d%m%Y').date()
        query = Curate_Query.objects.filter(curate_customer=curate_customer).filter(time_stamp=date_parsed).order_by("pk").last()
    suggestions = Curate_Query_Cluster.objects.filter(
            center__curate_query=query).order_by('rank')#.values_list('center', flat=True)
    #suggestions = Article_Curate_Query.objects.filter(curate_query=query).filter(rank__gt = 0).order_by("rank")
    #suggestions = [cluster.center for cluster in clusters]
    options = Curate_Customer_Selection.objects.filter(curate_customer=curate_customer).order_by("pk")
    if request.method == 'POST':
        config = configparser.RawConfigParser()
        config.read('curate/customers/' + key +
                         "/" + key + '.cfg')
        query.selection_made = True
        query.save()
        selected_articles = []
        for i in range(1, len(suggestions) + 1):
            for option in options:                    
                try:
                    xx = request.POST[option.name + str(i)]
                    if xx == 'on':
                        s = suggestions[i-1]
                        selected_articles.append({"title": s.center.article.title, "body": s.center.article.body[0:200], "selection": option.name})
                        for reason in option.rejection_reason.all():
                            try:
                                yy = request.POST[option.name + str(i) + reason.name]
                                print(yy)
                                if  yy == "on":
                                    if reason.kind == "sou":
                                        curate_customer.bad_source.add(s.center.article.source)
                                        curate_customer.save()
                                    else:
                                        reason.current_members.add(s.center)
                                        reason.save()
                                        if reason.kind == "con":
                                            s.center.bad_article = True
                            except:
                                pass
                        s.center.selection_options.add(option)
                        s.center.save()
                except:
                    pass
                    
        try:
            selection_made_task(key, selected_articles)
            selection_made_task.delay(key, selected_articles)
        except:
            pass
        try:
            print(im.get_env_variable('DJANGO_SETTINGS_MODULE'))
            print(config.getboolean('meta','direct_outlet'))
            if config.getboolean('meta','direct_outlet') and im.get_env_variable('DJANGO_SETTINGS_MODULE') == "conf.settings.deployment":
                send_newsletter_task.delay(key)
        except:
            pass

    stats = {}
    for option in options.all():
        stat = [i for i in suggestions if option in i.center.selection_options.all()]
        stats[option] = len(stat)
    context = {"stats": stats, "suggestions": suggestions, "options": options, 'query': query, 'customer_key': key}
    return render(request, 'curate/interface.html', context)

@login_required()
def mail(request, customer_key=None):
    if customer_key != None:
        print(customer_key)
        if request.user.is_superuser:
            key = customer_key
        else:
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                if not customer_key == user_profile.customer.customer_key:
                    return redirect('/login/?next=%s' % request.path)
            except:
                return redirect('/login/?next=%s' % request.path)
    else:
        print("None")
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            key = user_profile.customer.customer_key
        except:
            return redirect('/login/?next=%s' % request.path)

    customer = Customer.objects.get(customer_key=key)
    curate_customer = Curate_Customer.objects.get(customer=customer)
    query = Curate_Query.objects.filter(
        curate_customer=curate_customer).order_by("pk").last()
    config = configparser.RawConfigParser()
    config.read('curate/customers/' + key +
                "/" + key + '.cfg')

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
    
    lang = config.get(
            'general', 'language')
    ma = max(3,len(articles))
    keywords = keywords_from_articles(articles[0:ma],lang)

    context = {"articles": articles, "stats_dict": stats_dict, "keywords": ";".join(keywords)}
    return render(request, 'curate/mail_template.html', context)
