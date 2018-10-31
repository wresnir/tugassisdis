from django.urls import path, include
from . import views
from rest_framework import routers

urlpatterns = [
    path('quorum', views.quorumView),
    path('ping', views.pingView),
    path('register', views.registerView),
    path('getSaldo', views.getSaldoView),
    path('getTotalSaldo', views.getTotalSaldoView),
    path('transfer', views.transferView),
]