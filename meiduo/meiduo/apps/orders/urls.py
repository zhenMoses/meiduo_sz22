from django.conf.urls import url
from . import views
urlpatterns = [
    # 去结算
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view()),
    # 保存订单
    url(r'^orders/$', views.SaveOrderView.as_view()),
    # url(r'orders/(?P<order_id>\d+)/uncommentgoods/$',views.UnCommenOrdertView.as_view())
]