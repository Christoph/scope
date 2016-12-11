from django.shortcuts import render, redirect
from datetime import date
# Create your views here.

from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer
from scope.models import Customer, Article, UserProfile


def interface(request,customer_key):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if not customer_key == user_profile.customer.customer_key:
            return redirect('/login/?next=%s' % request.path)
    except:
        return redirect('/login/?next=%s' % request.path)

    customer = Customer.objects.get(customer_key=customer_key) #will be replaced by authentication
    curate_customer = Curate_Customer.objects.get(customer=customer)
    last_query = Curate_Query.objects.filter(curate_customer=curate_customer).filter(time_stamp=date.today()).order_by("pk").reverse()[0]
    article_query_instances = Article_Curate_Query.objects.filter(curate_query=last_query).filter(rank__gt = 0).order_by("rank")
    suggestions = article_query_instances

    selection_made = False
    try:
        if len(article_query_instances.filter(is_selected=True)) != 0:
            selection_made = True
    except:
        pass
    if request.method == 'POST':
        print request.POST

        # Check that sufficiently many articles have been chosen

        # extract those fields that have been checked.
        for i in range(1, len(suggestions) + 1):
            try:
                xx = request.POST['select' + str(i)]
                if xx == 'on':
                    s = suggestions[1][i-1]
                    s.is_selected = True
                    s.save()
                    selection_made = True
            except:
                pass
            try:
                xx = request.POST['mistake' + str(i)]
                if xx == 'on':
                    s = suggestions[1][i-1]
                    s.is_mistake = True
                    s.save()
            except:
                pass




    #log_inf, log_link = check_login(request)
    #context = {"suggestions":suggestions, 'log_inf':log_inf, 'log_link':log_link}
    context = {"suggestions": suggestions, 'selection_made': selection_made, 'customer_key': customer_key}
    return render(request, 'curate/interface.html', context)
