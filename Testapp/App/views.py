from django.shortcuts import render,HttpResponse

# Create your views here.

def getUrl(request):
    return HttpResponse("hello Django!")

def display_echarts(requres):
    return render(requres, 'App/getdata.html')
