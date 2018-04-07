from django.core.cache import cache
from django.shortcuts import render
from .models import GoodsCategory,IndexGoodsBanner,IndexPromotionBanner,IndexCategoryGoodsBanner,GoodsSKU
from django.http import Http404
from django_redis import get_redis_connection
from django.core.paginator import Paginator
from haystack.generic_views import SearchView
import json


# Create your views here.
def fdfs_test(request):
    category = GoodsCategory.objects.get(pk=1)
    context = {
        'category':category
    }
    return render(request,'fdfs.html',context)

def index(request):
    context = cache.get('index')
    if context is None:
        # 查询分类信息
        category_list = GoodsCategory.objects.all()

        # 查询轮播图片
        banner_list = IndexGoodsBanner.objects.all().order_by('index')

        # 查询广告
        adv_list = IndexPromotionBanner.objects.all().order_by('index')

        # 查询每个分类的推荐产品
        for category in category_list:
            # 查询推荐按的标题商品
            category.title_list = IndexCategoryGoodsBanner.objects.filter(display_type=0,category=category).order_by('index')[0:3]
            # 查询推荐的图片信息
            category.title_list = IndexCategoryGoodsBanner.objects.filter(display_type=1,category=category).order_by('index')[0:4]



        context = {
            'title':'首页',
            'category_list':category_list,
            'banner_list':banner_list,
            'adv_list':adv_list,
        }
        # 将context设为缓存
        cache.set('index',context,3600)

    context['total_count']=get_cart_total(request)

    response = render(request,'index.html',context)


    return response

def detail(request,sku_id):
    # 查询商品信息
    try:
        sku = GoodsSKU.objects.get(pk=sku_id)
    except:
        raise Http404()
    # 查询分类信息
    category_list = GoodsCategory.objects.all()

    # 查询新品推荐：当前商品所在分类的最新的两个商品
    # new_list = GoodsCategory.objects.filter(category=sku.category).order_by('id')[0:2]
    new_list = sku.category.goodssku_set.order_by('id')[0:2]

    # 查询当期那所有商品对应的所有陈列
    # 根据当前sku找到对应的spu
    goods = sku.goods
    # 根据spu找所有的sku
    other_list = goods.goodssku_set.all()

    if request.user.is_authenticated():
        # 最近浏览
        #  首先获取和redis的连接
        redis_client = get_redis_connection()
        # 构造列表键值（列表的名字）
        keys = 'history%d'%request.user.id
        # 如果当前商品编号已经存在，就先删除
        redis_client.lrem(keys,0,sku_id)
        #  向redis中放值
        redis_client.lpush(keys, sku_id)
        # 如果列表长度大于５，就删除最后一个
        if redis_client.llen(keys)>5:
            redis_client.rpop(keys)

    comment_list=sku.ordergoods_set.exclude(comment='')
    context = {
        'title':'商品详情',
        'sku': sku,
        'category_list': category_list,
        'new_list': new_list,
        'other_list': other_list,
        'comment_list': comment_list,
    }
    context['total_count'] = get_cart_total(request)
    return render(request,'detail.html',context)

def list_sku(request, category_id):
    # 查询当期分类对象
    try:
        category_now = GoodsCategory.objects.get(pk=category_id)
    except:
        raise Http404

    # 接受排序规则
    order = int(request.GET.get('order',1))
    if order==2:
        order_by='-price'
    elif order==3:
        order_by='price'
    elif order==4:
        order_by="-sales"
    else:
        order_by='-id'

    # 查询当前分类的所有商品
    sku_list = GoodsSKU.objects.filter(category=category_id).order_by(order_by)

    # 产讯所有分类信息
    category_list = GoodsCategory.objects.all()

    #　查询当前分类对应的最新的两个商品
    new_list = category_now.goodssku_set.all().order_by('-id')[0:2]

    # 分页
    paginator = Paginator(sku_list,1)
    # 接受页码值
    pindex = int(request.GET.get('pindex',1))
    total_page = paginator.num_pages

    if pindex < 1:
        pindex = 1
    if pindex > total_page:
        pindex = total_page
    page = paginator.page(pindex)

    # 构造页码的列表，用于返回页码的范围
    page_list = []
    if total_page <= 5:
        page_list = range(1, total_page + 1)

    elif pindex < 2:
        page_list = range(1,6)
    elif pindex >= total_page-1:
        page_list = range(total_page - 4, total_page + 1)
    else:
        page_list = range(pindex-2,pindex+3)


    context={
        'title':'商品列表页',
        'page': page,
        'category_list': category_list,
        'category_now': category_now,
        'new_list': new_list,
        'order': order,
        'page_list': page_list
    }
    context['total_count'] = get_cart_total(request)
    return render(request, 'list.html', context)

class MySearchView(SearchView):
    def get(self, request, *args, **kwargs):
        self.curr_request = request
        return super().get(request, *args, **kwargs)
    """My custom search view."""
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title']='搜索结果'
        context['category_list']=GoodsCategory.objects.all()
        context['total_count'] = get_cart_total(self.curr_request)
        # do something
        return context


def get_cart_total(request):
    '''获取购车车中商品的总数量'''
    total_count = 0
    if request.user.is_authenticated():
       redis_client = get_redis_connection()
       for v in redis_client.hvals('cart%d'%request.user.id):
           total_count += int(v)
    else:
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            cart_dict = json.loads(cart_str)
            for k,v in cart_dict.items():
                total_count += v
    return total_count

