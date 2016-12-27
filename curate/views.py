from django.shortcuts import render, redirect
from datetime import date
# Create your views here.

from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer, Curate_Customer_Selection
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
    query = Curate_Query.objects.filter(curate_customer=curate_customer).order_by("pk").last()
    article_query_instances = Article_Curate_Query.objects.filter(curate_query=query).filter(rank__gt = 0).order_by("rank")
    suggestions = article_query_instances
    options = Curate_Customer_Selection.objects.filter(curate_customer=curate_customer)
    if request.method == 'POST':
        query.selection_made = True
        query.save()

        for i in range(1, len(suggestions) + 1):
            for option in options:                    
                try:
                    xx = request.POST[option.name + str(i)]
                    if xx == 'on':
                        s = suggestions[i-1]
                        s.selection_options.add(option)
                        s.save()
                except:
                    pass

    #log_inf, log_link = check_login(request)
    #context = {"suggestions":suggestions, 'log_inf':log_inf, 'log_link':log_link}
    context = {"suggestions": suggestions, "options": options, 'query': query, 'customer_key': customer_key}
    return render(request, 'curate/interface.html', context)
