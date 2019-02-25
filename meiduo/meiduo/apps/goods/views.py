from django.shortcuts import render
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response

from goods.models import SKU
from goods.serializers import SKUSerializer, SKUCommentsSerializer
# Create your views here.
from orders.models import OrderGoods


class SKUListView(ListAPIView):
    """sku列表数据"""
    serializer_class = SKUSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('create_time', 'price', 'sales')

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id, is_launched=True)


class SKUComments(GenericAPIView):
    """sku评论"""
    serializer_class = SKUCommentsSerializer
    # 查询用户名数据

    def get(self, request, sku_id):
        queryset = OrderGoods.objects.filter(sku_id=sku_id, is_commented=True)
        for i in queryset:
            if i.is_anonymous:
                i.username = i.order.user.username.replace(i.order.user.username[1:-1], '******')
            else:
                i.username = i.order.user.username
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)





