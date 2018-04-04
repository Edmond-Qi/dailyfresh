import json

from django.shortcuts import render
from django.http import JsonResponse,Http404
from redis import client
from tt_goods.models import GoodsSKU
from django_redis import get_redis_connection

# Create your views here.
def add(request):
    '''
    添加到购物车
    党进行数据的添加、修改、删除时，一般采用的post方式
    '''
    if request.method != 'POST':
        return Http404

    dict = request.POST
    sku_id = dict.get('sku_id')
    count = int(dict.get('count', 0))

    # 验证数据有效性
    # 判断商品是否存在
    if GoodsSKU.objects.filter(id=sku_id).count() <= 0:
        return JsonResponse({'status':2})

    if count <= 0:
        return JsonResponse({'status':3})

    if count >= 5:
        count = 5


    if request.user.is_authenticated():
        # 如果用户已经登录，把购物车信息存储在redis中
        redis_client = get_redis_connection()
        key = 'cart%d' % request.user.id
        if redis_client.hexists(key, sku_id):
            # 　如果有则数量相加
            count1 = int(redis_client.hget(key, sku_id))
            count2 = count
            count0 = count1 + count2
            if count0 > 5:
                count0 = 5
            redis_client.hset(key, sku_id, count0)
        else:
            # 如果无则添加
            redis_client.hset(key, sku_id, count)

        total_count = 0
        for v in redis_client.hvals(key):
            total_count += int(v)
        return JsonResponse({'status': 1, 'total_count': total_count})

    else:
        # 如果未登录，把购物车信息存储在cookie中
        # 存储数据的格式：｛｝
        # 构造数据
        cart_dict = {}
        # 先从coookie中读取数据，如果cart_dict存在就解析出来，如果不存在就使用空字典
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            cart_dict = json.loads(cart_str)
            if sku_id in cart_dict:
                cart_dict[sku_id] += count
                if cart_dict[sku_id] > 5:
                    cart_dict[sku_id] = 5
            else:
                cart_dict[sku_id] = count

        # 计算商品总数量
        total_count = 0
        for k, v in cart_dict.items():
            total_count += v

        # 将字典转成字符串，用于存入cookie中
        cart_str = json.dumps(cart_dict)
        response = JsonResponse({'status': 1, 'total_count':total_count})
        response.set_cookie('cart',cart_str,expires=60*60*24*14)

    return response

def index(request):
    # 查询购物车中的商品信息
    sku_list = []
    if request.user.is_authenticated():
        redis_client = get_redis_connection()
        key = 'cart%d'%request.user.id
        id_list = redis_client.hkeys(key)
        for id1 in id_list:
            sku = GoodsSKU.objects.get(pk=id1)
            sku.count = int(redis_client.hget(key, id1))
            sku_list.append(sku)
    else:
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            cart_dict = json.loads(cart_str)
            for k, v in cart_dict.items():
                sku = GoodsSKU.objects.get(id=k)
                sku.count = v
                sku_list.append(sku)
    context={
        'title':'购物车',
        'sku_list':sku_list
    }


    return render(request, 'cart.html', context)

def edit(request):
    if (request.method != 'POST'):
        return Http404

    dict = request.POST
    sku_id = dict.get('sku_id',0)
    count = int(dict.get('count',0))

    # 验证数据的有效性
    # 判断商品是否存在
    if GoodsSKU.objects.filter(pk=sku_id).count() <= 0:
        return JsonResponse({'status':2})

    # 判断数量是否是一个有效数字
    try:
        count = int(count)
    except:
        return JsonResponse({'status':3})
    print(count)
    # 判断数量大于０并小于５
    if count <= 0:
        count = 1
    elif count >= 5:
        count = 5
    response = JsonResponse({'status': 1})
    # 改写购物车中的数量
    if request.user.is_authenticated():
        # 如果已经登陆，操作redis
        redis_client = get_redis_connection()
        key = 'cart%d'%request.user.id
        if redis_client.hexists(key,sku_id):
            redis_client.hset(key, sku_id, count)


    else:
        # 如果未登录操作cookie
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            cart_dict = json.loads(cart_str)
            # 改写数量
            cart_dict[sku_id] = count
            cart_str = json.dumps(cart_dict)
            response.set_cookie('cart', cart_str, expires=60*60*24*14)

    return response

def delete(request):
    if (request.method != 'POST'):
        return Http404

    dict = request.POST
    sku_id = dict.get('sku_id',0)

    # 验证数据的有效性
    # 判断商品是否存在
    if GoodsSKU.objects.filter(pk=sku_id).count() <= 0:
        return JsonResponse({'status':2})

    response = JsonResponse({'status': 1})
    # 改写购物车中的数量
    if request.user.is_authenticated():
        # 如果已经登陆，操作redis
        redis_client = get_redis_connection()
        key = 'cart%d'%request.user.id
        if redis_client.hexists(key,sku_id):
            redis_client.delete(key, sku_id)


    else:
        # 如果未登录操作cookie
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            cart_dict = json.loads(cart_str)
            # 改写数量
            cart_dict.pop(sku_id)
            cart_str = json.dumps(cart_dict)
            response.set_cookie('cart', cart_str, expires=60*60*24*14)

    return response