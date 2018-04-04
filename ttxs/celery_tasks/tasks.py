import os
# os.environ["DJANGO_SETTINGS_MODULE"] = "ttxs.settings"
# # 放到Celery服务器上时添加的代码
# import django
# django.setup()

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
from django.core.mail import send_mail
from celery import Celery
from tt_goods.models import GoodsCategory,Goods,GoodsSKU,GoodsImage,IndexCategoryGoodsBanner,IndexPromotionBanner,IndexGoodsBanner
from django.conf import settings
from django.shortcuts import render
import time

app=Celery('celery_tasks.tasks',broker='redis://127.0.0.1:6379/6')

@app.task
def send_user_active(id,email):
    # 加密用户编号
    serializer = Serializer(settings.SECRET_KEY, 60 * 60)
    value = serializer.dumps({'id': id}).decode()
    msg = '<a href="http://192.168.18.136:8000/user/active/%s">点击激活</a>' % value
    send_mail('天天生鲜-账户激活', '', settings.EMAIL_FROM, [email], html_message=msg)


@app.task
def say_ok():
    pass

@app.task
def generate_html():
    time.sleep(2)
    # 查询分类信息
    category_list = GoodsCategory.objects.all()

    # 查询轮播图片
    banner_list = IndexGoodsBanner.objects.all().order_by('index')

    # 查询广告
    adv_list = IndexPromotionBanner.objects.all().order_by('index')

    # 查询每个分类的推荐产品
    for category in category_list:
        # 查询推荐按的标题商品
        category.title_list = IndexCategoryGoodsBanner.objects.filter(display_type=0, category=category).order_by(
            'index')[0:3]
        # 查询推荐的图片信息
        category.title_list = IndexCategoryGoodsBanner.objects.filter(display_type=1, category=category).order_by(
            'index')[0:4]

    context = {
        'title': '首页',
        'category_list': category_list,
        'banner_list': banner_list,
        'adv_list': adv_list,
    }
    response = render(None, 'index.html', context)
    html = response.content.decode()
    # 将首页保存到文件中
    with open(os.path.join(settings.GENERATE_HTML, 'index.html'), 'w') as f1:
        f1.write(html)
