from django.views.generic import View
from django.contrib.auth.decorators import login_required

# 找到对应的视图函数,然后在视图函数上添加装饰器
# class LoginRequiredView(View):
#     @classmethod
#     def as_view(cls, **initkwargs):
#         func = super().as_view(**initkwargs)
#         return login_required(func)
 # 上面的代码将登陆验证与类视图进行了绑定


# 夺继承扩展类
class LoginRequiredViewMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        func = super().as_view(**initkwargs)
        return login_required(func)