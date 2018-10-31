from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .models import User
import requests
import json

SUCCESS = 1
USER_NOT_EXIST = -1
QUORUM_NOT_ENOUGH = -2
CALL_FAILED = -3
DATABASE_FAILED = -4
VALUE_NOT_VALID = -5
BALANCE_NOT_ENOUGH = -6
UNDEFINED = -99
THIS_IP = "172.22.0.203"
THIS_USER = "1406543896"

# Quorum dummy
# listTest = [
#     {"ip": "172.22.0.208","npm": "1406622856"},#rizqi
#     {"ip": "172.22.0.206","npm": "1406572340"},#papeng
#     {"ip": "172.22.0.205","npm": "1406571123"},#fakhri
#     {"ip": "172.22.0.203","npm": "1406543896"},#wresni
#     {"ip": "172.22.0.207","npm": "1406578205"} #irfan
# ]

listTest = [
    {"ip": "172.22.0.203","npm": "1406543896"},#wresni
    {"ip": "172.22.0.207","npm": "1406578205"} #irfan
]

# Create your views here.
@csrf_exempt
def quorum():
    # response = requests.get('http://172.22.0.222/lapors/list.php').json()
    response = listTest
    count = 0
    for domain in response:
        try:
            # raw_ping = requests.post('http://'+domain['ip']+'/ewallet/ping').json()
            raw_ping = requests.post('http://'+domain['ip']+'/ewallet/ping').json()
            if(raw_ping['pingReturn'] == SUCCESS):
                count += 1
        except:
            pass
    out = count/len(response)
    return out

@csrf_exempt
@api_view(['POST', ])
def pingView(request):
    res = {}
    try:
        res['pingReturn'] = SUCCESS
    except:
        res['pingReturn'] = UNDEFINED
    return Response(res)

@csrf_exempt
@api_view(['POST', ])
def registerView(request):
    req = request.data
    res = {}
    #Quorum check
    if quorum() <= 0.5:
        res['registerReturn'] = QUORUM_NOT_ENOUGH
        return Response(res)
    try:
        #Register process
        queryset = User(user_id=req['user_id'], nama=req['nama'], nilai_saldo=0)
        if req['user_id'] == THIS_USER:
            queryset.nilai_saldo = 1000000000
        queryset.save()
        res['registerReturn'] = SUCCESS
    except Exception as e:
        #If register process failed
        print(e)
        res['registerReturn'] = DATABASE_FAILED
    return Response(res)
    

@csrf_exempt
@api_view(['POST', ])
def getSaldoView(request):
    req = request.data
    res = {}
    #Quorum check
    if quorum() <= 0.5:
        res['saldo'] = QUORUM_NOT_ENOUGH
        return Response(res)
    try:
        #Get saldo process
        queryset = User.objects.get(user_id=req['user_id'])
        res['saldo'] = queryset.nilai_saldo
    except ObjectDoesNotExist as e:
        print(e)
        res['saldo'] = USER_NOT_EXIST
    except Exception as e:
        #If get saldo process failed
        print(e)
        res['saldo'] = DATABASE_FAILED
    return Response(res)

def totalSaldoExt(user_id):
    response = requests.get('http://172.22.0.222/lapors/list.php').json()
    out = 0
    for branch in response:
        if branch['npm'] == user_id:
            post_param = {}
            post_param['user_id'] = user_id
            req_post = requests.get('http://'+branch['ip']+'/ewallet/getTotalSaldo', post_param).json()
            out = req_post['saldo']
    return out

def totalSaldoIn(user_id):
    response = requests.get('http://172.22.0.222/lapors/list.php').json()
    balance = getSaldo(request).data
    out = balance['saldo']
    for branch in response:
        post_param = {}
        post_param['user_id'] = user_id
        req_post = requests.get('http://'+branch['ip']+'/ewallet/getSaldo', post_param).json()
        if req_post['saldo'] < 0:
            out += 0
        else:
            out += req_post['saldo']
    return out

@csrf_exempt
@api_view(['POST', ])
def getTotalSaldoView(request):
    req = request.data
    res = {}
    #Quorum check
    if quorum() < 1:
        res['saldo'] = QUORUM_NOT_ENOUGH
        return Response(res)
    try:
        queryset = User.objects.get(user_id=req['user_id'])
        res['saldo'] = totalSaldoIn(req['user_id'])
    except ObjectDoesNotExist as e:
        res['saldo'] = totalSaldoExt(req['user_id'])
    except Exception as e:
        res['saldo'] = DATABASE_FAILED
    return Response(res)

@csrf_exempt
@api_view(['POST', ])
def transferView(request):
    req = request.data
    res = {}
    #Quorum check
    if quorum() <= 0.5:
        res['saldo'] = QUORUM_NOT_ENOUGH
        return Response(res)
    if req['nilai'] < 0 or req['nilai'] > 1000000000:
        res['saldo'] = VALUE_NOT_VALID
        return Response(res)
    try:
        queryset = User.objects.get(user_id=req['user_id'])
        queryset.nilai_saldo += req['nilai']
        queryset.save()
        res['transferReturn'] = SUCCESS
    except ObjectDoesNotExist as e:
        res['transferReturn'] = USER_NOT_EXIST
    except Exception as e:
        res['saldo'] = DATABASE_FAILED
    return Response(res)

@csrf_exempt
@api_view(['POST', ])
def transferToView(request):
    req = request.data
    res = {}
    # Check saldo
    balance = getSaldo(request).data
    if balance < 0:
        res['status'] = balance['saldo']
        return Response(res)
    elif balance < req['nilai']:
        res['status'] = BALANCE_NOT_ENOUGH
        return Response(res)

    # Check target
    target_param = {}
    target_param['user_id'] = req['user_id']
    target = request.post('http://'+branch['ip']+'/ewallet/getSaldo', target_param).json()['saldo']
    if saldo < 0:
        register_param = {}
        register_param['user_id'] = req['user_id']
        register_param['nama'] = ""
        register_res = request.post('http://'+branch['ip']+'/ewallet/getSaldo', register_param).json()
    
    transfer_param = {}
    transfer_param['user_id'] = req['user_id']
    transfer_param['nilai'] = req['nilai']
    transfer = request.post('http://'+branch['ip']+'/ewallet/getSaldo', transfer_param).json()['transferReturn']
    if transfer == SUCCESS:
        queryset = User.objects.get(user_id=req['user_id'])
        queryset.nilai_saldo -= req['nilai']
        queryset.save()
        res['status'] = SUCCESS
    else:
        res['status'] = transfer
    return Response(res)