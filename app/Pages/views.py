from django.shortcuts import render_to_response, HttpResponseRedirect
from django.http import HttpResponse

# Create your views here.
def home(request):
    if not request.method == 'GET':
        HttpResponseRedirect('home.html')

    parameter = request.GET
    if len(parameter) != 0:
        quary = parameter['q']
        return render_to_response('result.html');
    else:
        return render_to_response('home.html')
