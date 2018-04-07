from django.conf.urls import url
from . import views

urlpatterns =[
    url(r'^$',views.index),
    url(r'^handle$', views.handle),
    url(r'^pay$',views.pay),
    url(r'^query$', views.query)
]