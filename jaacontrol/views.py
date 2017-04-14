from django.shortcuts import render
from django.shortcuts import redirect
import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
# Create your views here.
from django.views.decorators.cache import never_cache

@never_cache
def index(request):
    if 'token' in request.COOKIES.keys():
        return render(request, 'jaacontrol/index.html', context={"name":"dashboard", "token": request.COOKIES['token']})
    else:
        return render(request, 'jaacontrol/index.html', context={"name":"dashboard", "token": "0"})
@never_cache
def player(request):
    if 'token' in request.COOKIES.keys():
        return render(request, 'jaacontrol/PlayerControl.html', context={"name":"player", "token": request.COOKIES['token']})
    else:
        return render(request, 'jaacontrol/PlayerControl.html', context={"name":"player", "token": "0"})

def login(request, token):
    response = redirect('/jaacontrol/')
    response.set_cookie('token', token)
    return response


def stuff(request):
    if 'token' in request.COOKIES.keys():
        return render(request, 'jaacontrol/stuff.html', context={"name":"stuff", "token": request.COOKIES['token']})
    else:
        return render(request, 'jaacontrol/stuff.html', context={"name":"stuff", "token": "0"})
