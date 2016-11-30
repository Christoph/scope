from django.shortcuts import render
from datetime import date
# Create your views here.

from curate.models import *
from curate.feeds import *


def interface(request):
    existingfeed = 0
    if request.user.is_authenticated():
        # User ALSO HAS TO BE NH!
        user_id = request.user.id

    else:
        user_id = None
        # if this is a POST request we need to process the form data

    selection_made = False
    suggestions = Select_NH.objects.filter(
        timestamp=date.today()).order_by('rank')
    try:
        if len(suggestions.filter(is_selected=True)) != 0:
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
                    q = suggestions[i - 1]
                    q.is_selected = True
                    q.save()
            except:
                pass
            try:
                xx = request.POST['mistake' + str(i)]
                if xx == 'on':
                    q = suggestions[i - 1]
                    q.is_mistake = True
                    q.save()
            except:
                pass

        selection_made = True

    #log_inf, log_link = check_login(request)
    #context = {"suggestions":suggestions, 'log_inf':log_inf, 'log_link':log_link}
    context = {"suggestions": suggestions, 'selection_made': selection_made}
    return render(request, 'nh/interface.html', context)
