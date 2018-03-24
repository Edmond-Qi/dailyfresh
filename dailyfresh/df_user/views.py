from django.shortcuts import render,redirect
from django.http import JsonResponse
from hashlib import sha1
from .models import *

def login(request):
    return render(request,'df_user/login.html')

def register(request):
    return render(request,'df_user/register.html')

def register_handle(request):
    # 获取用户输入
    post = request.POST
    uname = post.get('user_name')
    upwd = post.get('pwd')
    upwd2 = post.get('cpwd')
    uemail = post.get('email')

    #判断两次密码
    if upwd!=upwd2:
        return redirect('/user/register/')

    #密码加密
    s1 = sha1()
    s1.update(upwd)
    upwd3 = s1.hexdigest()

    #校验通过，开始创建对象
    user = UserInfo()
    user.uname = uname
    user.upwd = upwd3
    user.uemail = uemail

    #注册成功转到登陆也页面
    return redirect('/user/login/')

def register_exist(request):
    uname = request.GET.get('uname')
    count = UserInfo.objects.filter(uname=uname).count()
    # json的参数和返回值都是ｊｓｏｎ
    return JsonResponse({'count':count})





