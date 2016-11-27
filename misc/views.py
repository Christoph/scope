from django.shortcuts import render

# Create your views here.
def artsy(request):
    return render(request, 'misc/artsy_rects_upon_suggest.html') #-{'topic': topic})
