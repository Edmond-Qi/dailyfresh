from django.db import models

class UserInfo(models.Model):
    uname = models.CharField(max_length=20)
    upwd = models.CharField(max_length=40)
    uemail = models.CharField(max_length=30)
    ushou = models.CharField(max_length=20,default='')
    uaddress = models.CharField(max_length=10,default='')
    uyoubian = models.CharField(max_length=6,default='')
    uphone = models.CharField(max_length=11,default='')
    #default,blank是python层面实现的，不影响数据库层的表结构