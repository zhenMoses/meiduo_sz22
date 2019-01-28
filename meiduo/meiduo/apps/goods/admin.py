from django.contrib import admin

from . import models

# Register your models here.
admin.site.register(models.GoodsCategory)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Goods)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU)
admin.site.register(models.SKUSpecification)
admin.site.register(models.SKUImage)


class xxx(admin.ModelAdmin):
    # 模型站点管理类,不光可以控制admin的页面展示样式,还可以监听它里面的数据变化

