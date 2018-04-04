from django.contrib import admin
from django.core.cache import cache

from .models import GoodsCategory,Goods,GoodsSKU,GoodsImage,IndexCategoryGoodsBanner,IndexPromotionBanner,IndexGoodsBanner
from celery_tasks.tasks import generate_html

class BaseAdmin(admin.ModelAdmin):
    # 当数据发生添加、修改、删除时，就会生成静态文件
    # 当添加对象、修改对象时，这个方法会被调用
    def save_model(self, request, obj, form, change):
        # super().save_model(request, obj, form, change)
        obj.save()
        generate_html.delay()
        # 删除缓存
        cache.delete()

    def delete_model(self, request, obj):
        # super().delete_model(request, obj)
        # 如果调用父类的方法，celery会比保存和删除方法快
        obj.delete()
        generate_html.delay()
        cache.delete()


class GoodsCategoryAdmin(BaseAdmin):
    list_display = ['id','name','logo']

class GoodsAdmin(BaseAdmin):
    pass

class GoodsSKUAdmin(BaseAdmin):
    pass

class GoodsImageAdmin(BaseAdmin):
    pass

class IndexCategoryGoodsBannerAdmin(BaseAdmin):
    pass

class IndexPromotionBannerAdmin(BaseAdmin):
    pass

class IndexGoodsBannerAdmin(BaseAdmin):
    pass


admin.site.register(GoodsCategory, GoodsCategoryAdmin)
admin.site.register(Goods, GoodsAdmin)
admin.site.register(GoodsSKU, GoodsSKUAdmin)
admin.site.register(GoodsImage, GoodsImageAdmin)
admin.site.register(IndexCategoryGoodsBanner, IndexCategoryGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)