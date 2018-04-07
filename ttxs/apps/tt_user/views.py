from django.shortcuts import render, redirect
from django.views.generic import View
from .models import User, Address,AreaInfo
import re
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
from celery_tasks.tasks import send_user_active
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from utils.views import LoginRequiredViewMixin
from django_redis import get_redis_connection
from tt_goods.models import GoodsSKU
import json
from tt_order.models import OrderInfo
from django.core.paginator import Paginator
from utils.page_list import get_page_list


# Create your views here.
class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html',{'title':'注册'})

    def post(self, request):
        # 　接收数据
        dict = request.POST
        uname = dict.get('user_name')
        pwd = dict.get('pwd')
        cpwd = dict.get('cpwd')
        email = dict.get('email')
        uallow = dict.get('allow')

        # 构造返回的数据
        context = {
            'uname': uname,
            'pwd': pwd,
            'email': email,
            'err_msg': '',
            'title': '注册处理'
        }

        # 　判断数据的有效性
        if uallow is None:
            context['err_msg'] = '请接受协议'
            return render(request, 'register.html', context)

        if not all([uname, pwd, cpwd, email]):
            context['err_msg'] = '请填写完整信息'
            return render(request, 'register.html', context)

        if pwd != cpwd:
            context['err_msg'] = '两次填写的密码不一致'
            return render(request, 'register.html', context)

        if User.objects.filter(username=uname).count() > 0:
            context['err_msg'] = '用户名重复'
            return render(request, 'register.html', context)

        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            context['err_msg'] = '邮箱格式不正确'
            return render(request, 'register.html', context)

        if User.objects.filter(email=email).count() > 0:
            context['err_msg'] = '该邮箱已注册'
            return render(request, 'register.html', context)

        # 保存对象
        user = User.objects.create_user(uname, email, pwd)
        user.is_active = False
        user.save()
        # 加密用户编号
        # serializer = Serializer(settings.SECRET_KEY, 60 * 60)
        # value = serializer.dumps({'id': user.id}).decode()
        # msg = '<a href="http://127.0.0.1:8000/user/active/%s">点击激活</a>' % value
        # send_mail('天天生鲜-账户激活','',settings.EMAIL_FROM,[email],html_message=msg)
        send_user_active.delay(user.id, user.email)

        # 提示
        return HttpResponse('注册成功，请稍候到邮箱中激活账户')


def active(request, value):
    try:
        serializer = Serializer(settings.SECRT_KEY)
        dict = serializer.loads(value)
    except SignatureExpired:
        return HttpResponse('链接已经过期')

    uid = dict.get('id')
    user = User.objects.get(pk=uid)
    user.is_active = True
    user.save()

    return redirect('/user/login/')


def exists(request):
    # 接收用户名
    uname = request.GET.get('uname')

    if uname is not None:
        # 判断用户名是否存在
        result = User.objects.filter(username=uname).count()

    # 返回结果
    return JsonResponse({'result': result})


class LoginView(View):
    def get(self, request):
        uname = request.COOKIES.get('uname', '')
        context = {
            'title': '登陆',
            'uname': uname
        }
        return render(request, 'login.html', context)

    def post(self, request):
        # 接收数据
        dict = request.POST
        uname = dict.get('username')
        upwd = dict.get('pwd')
        remember = dict.get('remember')

        # 构造返回结果
        context = {
            'uname': uname,
            'upwd': upwd,
            'err_msg': '',
            'title': '登录处理',
        }

        # 判断数据是否填写
        if not all([uname, upwd]):
            context['err_msg'] = '请填写完整信息'
            return render(request, 'login.html', context)

        # 判断用户名、密码是否正确
        user = authenticate(username=uname, password=upwd)

        if user is None:
            context['err_msg'] = '用户名或密码错误'
            return render(request, 'login.html', context)

        # 如果未激活也不允许登录
        if not user.is_active:
            context['err_msg'] = '请先到邮箱中激活'
            return render(request, 'login.html', context)

        # 状态保持
        login(request, user)

        #取next参数，转回到之前的页面
        next_url = request.GET.get('next', '/user/info')
        response = redirect(next_url)

        # 记住用户名
        if remember is None:
            response.delete_cookie('uname')
        else:
            response.set_cookie('uname', uname, expires=60 * 60 * 24)


        # 1.读取cookie中的购物车信息，转成字典
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            key = 'cart%d' % request.user.id
            # 将cookies中的购物车信息转存入redis中
            redis_client = get_redis_connection()
            cart_dict = json.loads(cart_str)
            for k,v in cart_dict.items():
                if redis_client.hexists(key,k):
                    #　如果有则数量相加
                    count1=int(redis_client.hget(key,k))
                    count2 = v
                    count0 = count1 + count2
                    if count0 > 5:
                        count0 = 5
                    redis_client.hset(key, k, count0)
                else:
                    # 如果无则添加
                    redis_client.hset(key,k,v)
            response.delete_cookie('cart')
        # 如果登录成功则转到用户中心页面
        return response


# 用户登录视图，用于清除用户的登陆信息
def logout_user(request):
    logout(request)
    return redirect('/user/login')


# 用于显示用户登陆后的页面，该视图可以展示用户相关信息
@login_required
def info(request):
    address = request.user.address_set.filter(isDefault=True)
    if address:
        address = address[0]
    else:
        address = None

    #获取redis服务器的连接
    redis_client = get_redis_connection()
    #用键区分用户的ｉｄ
    good_list = redis_client.lrange('history%d'%request.user.id,0,-1)
    #根据商品编号查询商品对象
    goods_list = []
    for gid in good_list:
        goods_list.append(GoodsSKU.objects.get(pk=gid))

    context = {
        'title':'个人信息',
        'address': address,
        'goods_list':goods_list
    }
    return render(request, 'user_center_info.html', context)


# 显示用户的订单信息
@login_required
def order(request):
    # 查询当前用户的所有订单数据、
    order_list = OrderInfo.objects.filter(user=request.user).order_by('-add_date')
    # 分页
    paginator = Paginator(order_list,2)
    total_page = paginator.num_pages
    pindex = int(request.GET.get('pindex',1))
    if pindex <= 1:
        pindex = 1
    if pindex >= total_page:
        pindex = total_page

    page = paginator.page(pindex)

    page_list = get_page_list(total_page,pindex)
    context = {
        'title':'我的订单',
        'page':page,
        'page_list':page_list
    }
    return render(request, 'user_center_order.html', context)


# 定义用户地址信息相关的视图
class SiteView(LoginRequiredViewMixin, View):
    def get(self,request):
        # 查询当前用户的收货地址
        addr_list = Address.objects.filter(user=request.user)
        context = {
            'title':'收货地址',
            'addr_list':addr_list

        }
        return render(request, 'user_center_site.html', context)
    def post(self,request):
        # 接收数据
        dict = request.POST
        receiver = dict.get('receiver')
        provice = dict.get('province')  # 选中的option的value值
        city = dict.get('city')
        district = dict.get('district')
        addr = dict.get('addr')
        code = dict.get('code')
        phone = dict.get('phone')
        default = dict.get('default')

        # 验证有效性
        if not all([receiver, provice, city, district, addr, code, phone]):
            return render(request, 'user_center_site.html', {'err_msg': '信息填写不完整'})

        # 保存数据
        address = Address()
        address.receiver = receiver
        address.province_id = provice
        address.city_id = city
        address.district_id = district
        address.addr = addr
        address.code = code
        address.phone_number = phone
        if default:
            address.isDefault = True
        address.user = request.user
        address.save()

        # 返回结果
        return redirect('/user/site')


# 查询并返回省市区
def area(request,index):
    if index is '':
        addr = AreaInfo.objects.filter(aParent__isnull=True)
    else:
        addr = AreaInfo.objects.filter(aParent=index)
    addr_list = []
    for item in addr:
        addr_list.append({'id':item.id, 'title':item.title})
    return JsonResponse({'list':addr_list})

class CommentView(LoginRequiredViewMixin, View):
    def get(self, request):
        order_id = request.GET.get('order_id')

        order = OrderInfo.objects.get(pk=order_id)
        context = {
            'title': '评论商品',
            'order':order,
        }
        return render(request, 'user_center_comment.html', context)

    def post(self, request):
        #虽然当前请求方式为post，但是order_id是在地址中的参数，所以使用GET来接收
        order_id = request.GET.get('order_id')

        order = OrderInfo.objects.get(pk=order_id)
        order.status = 5
        order.save()

        dict = request.POST

        for detail in order.ordergoods_set.all():
            detail.comment = dict.get(str(detail.id))
            detail.save()
        return redirect('/user/order')
