from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
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
    response = requests.get('http://172.22.0.222/lapors/list.php').json()
    # response = listTest
    count = 0
    for domain in response:
        try:
            raw_ping = requests.post('http://'+domain['ip']+'/ewallet/ping').json()
            if(raw_ping['pingReturn'] == SUCCESS):
                count += 1
        except:
            pass
    out = count/len(response)
    return out

@csrf_exempt
@api_view(['POST', ])
def quorumView(request):
    res = {}
    res['quorum'] = quorum()
    return Response(res)

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
    req = json.loads(bytes.decode(request.body))
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
    except MultiValueDictKeyError as e:
        res['registerReturn'] = UNDEFINED
    except Exception as e:
        #If register process failed
        print(e)
        res['registerReturn'] = DATABASE_FAILED
    return Response(res)
    

@csrf_exempt
@api_view(['POST', ])
def getSaldoView(request):
    req = json.loads(bytes.decode(request.body))
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
    except MultiValueDictKeyError as e:
        res['saldo'] = UNDEFINED
    except Exception as e:
        #If get saldo process failed
        print(e)
        res['saldo'] = DATABASE_FAILED
    return Response(res)

def totalSaldoExt(user_id):
    response = requests.get('http://172.22.0.222/lapors/list.php').json()
    # response = listTest
    post_param = {}
    post_param['user_id'] = user_id
    post_param = json.dumps(post_param)
    out = -1
    for branch in response:
        if branch['npm'] == user_id:
            req_post = requests.post('http://'+branch['ip']+'/ewallet/getTotalSaldo', post_param).json()
            out = req_post['saldo']
            break
    return out

def totalSaldoIn(user_id):
    response = requests.get('http://172.22.0.222/lapors/list.php').json()
    # response = listTest
    post_param = {}
    post_param['user_id'] = user_id
    post_param = json.dumps(post_param)
    out = 0
    for branch in response:
        req_post = requests.post('http://'+branch['ip']+'/ewallet/getSaldo', post_param).json()
        if req_post['saldo'] == DATABASE_FAILED:
            out = DATABASE_FAILED
            break
        elif req_post['saldo'] < 0:
            out += 0
        else:
            out += req_post['saldo']
    return out

@csrf_exempt
@api_view(['POST', ])
def getTotalSaldoView(request):
    req = json.loads(bytes.decode(request.body))
    res = {}
    #Quorum check
    if quorum() < 1:
        res['saldo'] = QUORUM_NOT_ENOUGH
        return Response(res)
    try:
        queryset = User.objects.get(user_id=req['user_id'])
        res['saldo'] = totalSaldoIn(req['user_id'])
    except ObjectDoesNotExist as e:
        if req['user_id'] == THIS_USER:
            res['saldo'] = USER_NOT_EXIST
        else:
            res['saldo'] = totalSaldoExt(req['user_id'])
    except Exception as e:
        print(e)
        res['saldo'] = DATABASE_FAILED
    return Response(res)

@csrf_exempt
@api_view(['POST', ])
def transferView(request):
    req = json.loads(bytes.decode(request.body))
    res = {}
    #Quorum check
    if quorum() <= 0.5:
        res['saldo'] = QUORUM_NOT_ENOUGH
        return Response(res)
    try:
        if req['nilai'] < 0 or req['nilai'] > 1000000000:
            res['saldo'] = VALUE_NOT_VALID
            return Response(res)
    except:
        res['saldo'] = UNDEFINED
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
    req = json.loads(bytes.decode(request.body))
    res = {}
    # Check saldo
    post_param = {}
    post_param['user_id'] = req['user_id']
    post_param = json.dumps(post_param)
    balance = requests.post('http://'+req['ip']+'/ewallet/getSaldo', post_param).json()['saldo']
    if balance < 0:
        res['status'] = balance['saldo']
        return Response(res)
    elif balance < req['nilai']:
        res['status'] = BALANCE_NOT_ENOUGH
        return Response(res)

    # Check target
    saldo = requests.post('http://'+req['ip']+'/ewallet/getSaldo', post_param).json()['saldo']
    if saldo < 0:
        register_param = {}
        register_param['user_id'] = req['user_id']
        register_param['nama'] = ""
        register_param = json.dumps(register_param)
        register_res = requests.post('http://'+req['ip']+'/ewallet/register', register_param).json()
    
    transfer_param = {}
    transfer_param['user_id'] = req['user_id']
    transfer_param['nilai'] = req['nilai']
    transfer_param = json.dumps(transfer_param)
    transfer = requests.post('http://'+req['ip']+'/ewallet/transfer', transfer_param).json()['transferReturn']
    if transfer == SUCCESS:
        queryset = User.objects.get(user_id=req['user_id'])
        queryset.nilai_saldo -= req['nilai']
        queryset.save()
        res['status'] = SUCCESS
    else:
        res['status'] = transfer
    return Response(res)