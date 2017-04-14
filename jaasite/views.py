from django.shortcuts import redirect
import requests
from django.http import HttpResponse
import json

def redirect_jaacontrol(request):
    return redirect('/jaacontrol/')

def api(request):

    key = request.GET.get('code', '')
    r = requests.post('https://api.quizlet.com/oauth/token',
                 params={'grant_type':'authorization_code',
                       'code':key,
                       'redirect_url':'http://139.59.211.4:8000/api/'},
                 auth=('pAW73kqeW9', 'fxgfjxYqFUbfGKCGQg8WEb'))
    resp = json.loads(r.text)

    # AAARGH THIS IS ALL FOR NOTHING PUVLIC ACCESS CALL IS ENOUGH
    # JFIOREJGJREWIOGJ
    return HttpResponse(r.text)
