from django.shortcuts import render

def heatmap(request):
    return render(request,'research/mi/heatmap.html')