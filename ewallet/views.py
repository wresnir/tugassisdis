from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .models import Repo
from .models import User
from .serializers import RepoSerializer
import requests
import json

# Create your views here.
class RepoView(viewsets.ModelViewSet):
    queryset = Repo.objects.all()
    serializer_class = RepoSerializer

listTest = [
    {"ip": "172.22.0.208","npm": "1406622856"},#rizqi
    {"ip": "172.22.0.206","npm": "1406572340"},#papeng
    {"ip": "172.22.0.205","npm": "1406571123"},#fakhri
    {"ip": "172.22.0.203","npm": "1406543896"},#wresni
    {"ip": "172.22.0.207","npm": "1406578205"} #irfan
]

@csrf_exempt
def quorum():
    response = requests.get('http://172.22.0.222/lapors/list.php').json()
    count = 0
    for domain in listTest:
        raw = json.loads(domain)
        ip = raw['ip']
        try:
            raw_ping = requests.post('http://'+ip+':8000/ewallet/ping').json()
            if(raw_ping['pingReturn'] == 1):
                count += 1
        except:
            count = count
    out = count/len(response)
    return out

@csrf_exempt
@api_view(['POST', ])
def pingView(request):
    res = {}
    res['pingReturn'] = 1
    return Response(res)

@csrf_exempt
@api_view(['POST', ])
def registerView(request):
    try:
        req = json.loads(request.body)
    except:
        req = json.loads(bytes.decode(request.body))
    res = {}
    #Quorum check
    if quorum() <= 0.5:
        res['registerReturn'] = -2
        return Response(res)
    try:
        #Register process
        queryset = User(user_id=req['user_id'], nama=req['nama'], nilai_saldo=0)
        queryset.save()
        res['registerReturn'] = 1
        return Response(res)
    except:
        #If register process failed
        res['registerReturn'] = -4
        return Response(res)
    

@csrf_exempt
@api_view(['POST', ])
def getSaldoView(request):
    req = json.loads(request.body)
    res = {}
    #Quorum check
    if quorum() <= 0.5:
        res['saldo'] = -2
        return Response(res)
    try:
        #Get saldo process
        queryset = User.objects.get(user_id=req['user_id'])[0]
        if not queryset:
            res['saldo'] = -1
        else:
            res['saldo'] = queryset.values('nilai_saldo')
    except:
        #If get saldo process failed
        res['saldo'] = -4
    return Response(res)

def totalSaldoExt(user_id):
    response = requests.get('http://172.22.0.222/lapors/list.php').json()
    out = 0
    for branch in response:
        if branch['npm'] == user_id:
            post_param = {}
            post_param['user_id'] = user_id
            req_post = requests.get('http://'+branch['ip']+':8000/ewallet/getTotalSaldo', post_param).json()
            out = req_post
    return out

def totalSaldoIn(user_id):
    response = requests.get('http://172.22.0.222/lapors/list.php').json()
    out = 0
    for branch in response:
        post_param = {}
        post_param['user_id'] = user_id
        req_post = requests.get('http://'+branch['ip']+':8000/ewallet/getSaldo', post_param).json()
        if req_post['saldo'] < 0:
            out += 0
        else:
            out += req_post['saldo']
    return out

@csrf_exempt
@api_view(['POST', ])
def getTotalSaldoView(request):
    req = json.loads(request.body)
    res = {}
    #Quorum check
    if quorum() < 1:
        res['saldo'] = -2
        return Response(res)
    try:
        queryset = User.objects.get(user_id=req['user_id'])[0]
        if not queryset:
            # TODO - implement track and call to other branch
            res['saldo'] = totalSaldoExt(req['user_id'])
        else:
            # TODO - Implement sum all balance from all branch
            res['saldo'] = totalSaldoIn(req['user_id'])
    except:
        res['saldo'] = -4
    return Response(res)

@csrf_exempt
@api_view(['POST', ])
def transferView(request):
    req = json.loads(request.body)
    res = {}
    #Quorum check
    if quorum() <= 0.5:
        res['saldo'] = -2
        return Response(res)
    saldo_raw = json.loads(getSaldoView(request))
    saldo = saldo_raw['saldo']
    if saldo != -1:
        if req['nilai'] > 1000000000:
            res['transferReturn'] = -5
        else:
            queryset = User.objects.get(user_id=req['user_id'])
    else:
        res['transferReturn'] = -1
    return Response(res)