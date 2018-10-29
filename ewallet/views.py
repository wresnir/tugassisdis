from django.shortcuts import render
from rest_framework import viewsets
from .models import Repo
from .serializers import RepoSerializer
import requests

# Create your views here.
class RepoView(viewsets.ModelViewSet):
    queryset = Repo.objects.all()
    serializer_class = RepoSerializer

def quorumView(request):
    response = requests.get('http://172.22.0.222/lapors/list.php')
    data_list = response.json()
    count = 0
    return data_list