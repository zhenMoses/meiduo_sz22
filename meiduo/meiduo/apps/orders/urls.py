
from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views


urlpatterns = [
    # 去结算
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view()),
    # 保存订单
    url(r'^orders/$', views.CommitOrderView.as_view()),
    #  订单商品评论
    url(r'^orders/(?P<order_id>\d+)/uncommentgoods/$', views.GoodsUncomments.as_view()),
    url(r'^orders/(?P<order_id>\d+)/comments/$', views.GoodsComment.as_view()),
]

