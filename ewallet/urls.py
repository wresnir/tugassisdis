from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('repos', views.RepoView, base_name='Repo')

urlpatterns = [
    path('', include(router.urls)),
    path('list', views.quorumView),
]