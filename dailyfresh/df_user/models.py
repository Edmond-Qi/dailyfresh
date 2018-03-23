from django.db import models

class UserInfo(models.Model):
    uname = models.CharField(max_length=20)
    upwd = models.CharField(max_length=40)
    uemail = models.CharField(max_length=30)
    ushou = models.CharField(max_length=20)
    uaddress = models.CharField(max_length=10)
    uyoubian = models.CharField(max_length=6)
    uphone = models.CharField(max_length=11)
