from django.db import models

# Create your models here.
class Repo(models.Model):
    ip = models.CharField(max_length=15)
    npm = models.CharField(max_length=10)

class User(models.Model):
    user_id = models.CharField(max_length=10, unique=True)
    nama = models.CharField(max_length=50, default='')
    nilai_saldo = models.IntegerField()