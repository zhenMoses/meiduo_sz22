from django.conf.urls import url
from . import views

urlpatterns = [

    # 商品列表界面
    url(r'^categories/(?P<category_id>\d+)/skus/$', views.SKUListView.as_view()),
    # 商品评论
    url(r'^skus/(?P<sku_id>\d+)/comments/$', views.SKUComments.as_view()),
]