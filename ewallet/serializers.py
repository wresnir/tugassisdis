from rest_framework import serializers
from .models import Repo
from .models import User

class RepoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repo
        fields = ('ip', 'npm')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('user_id', 'nama', 'saldo')