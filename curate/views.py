from django.shortcuts import render, redirect
from datetime import datetime
# Create your views here.

from curate.models import Curate_Query, Article_Curate_Query, Curate_Customer, Curate_Customer_Selection, Curate_Rejection_Reasons
from scope.models import Customer, UserProfile


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
        print date_parsed
        query = Curate_Query.objects.filter(curate_customer=curate_customer).filter(time_stamp=date_parsed).order_by("pk").last()
    suggestions = Article_Curate_Query.objects.filter(curate_query=query).filter(rank__gt = 0).order_by("rank")
    options = Curate_Customer_Selection.objects.filter(curate_customer=curate_customer)
    if request.method == 'POST':
        print request.POST
        # query.selection_made = True
        # CHANGE THIS BACK
        #query.save()

        for i in range(1, len(suggestions) + 1):
            for option in options:                    
                try:
                    xx = request.POST[option.name + str(i)]
                    if xx == 'on':
                        s = suggestions[i-1]
                        try:
                            for reason in option.rejection_reason.all():
                                if request.POST[option.name + str(i) + reason.name] == "on":
                                    if reason.type == "sou":
                                        curate_customer.bad_source.add(s.article.source)
                                        curate_customer.save()
                                    elif reason.type == "con":
                                        #train classifier
                                        pass
                                    elif reason.type == "frq":
                                        curate_customer.too_frequent.add(s)
                                        curate_customer.save()
                                        #add to frequency selector
                                        pass
                        except:
                            pass
                        s.selection_options.add(option)
                        s.save()
                except:
                    pass
    stats = {}
    for option in options.all():
        stat = [i for i in suggestions if option in i.selection_options.all()]
        stats[option] = len(stat)
    context = {"stats": stats, "suggestions": suggestions, "options": options, 'query': query, 'customer_key': customer_key}
    return render(request, 'curate/interface.html', context)
