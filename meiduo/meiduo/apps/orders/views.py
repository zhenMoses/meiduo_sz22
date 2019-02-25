from django.db import transaction
from django.shortcuts import render
from rest_framework import serializers, status
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_redis import get_redis_connection
from decimal import Decimal
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, GenericAPIView, UpdateAPIView

from goods.models import SKU
from orders.models import OrderGoods, OrderInfo
from users.serializers import OrderGoodSerializer
from .serializers import OrderSettlementSerializer, CommitOrderSerializer, GoodsComments


# Create your views here.
class CommitOrderView(CreateAPIView):

    # 指定权限
    permission_classes = [IsAuthenticated]

    # 指定序列化器
    serializer_class = CommitOrderSerializer


class OrderSettlementView(APIView):
    """去结算接口"""

    permission_classes = [IsAuthenticated]  # 给视图指定权限

    def get(self, request):
        """获取"""
        user = request.user

        # 从购物车中获取用户勾选要结算的商品信息
        redis_conn = get_redis_connection('cart')
        redis_cart = redis_conn.hgetall('cart_%s' % user.id)
        cart_selected = redis_conn.smembers('selected_%s' % user.id)

        cart = {}
        for sku_id in cart_selected:
            cart[int(sku_id)] = int(redis_cart[sku_id])

        # 查询商品信息
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]

        # 运费
        freight = Decimal('10.00')
        # 创建序列化器时 给instance参数可以传递(模型/查询集(many=True) /字典)
        serializer = OrderSettlementSerializer({'freight': freight, 'skus': skus})

        return Response(serializer.data)


class GoodsUncomments(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderGoodSerializer

    def get(self, request, order_id):
        user = self.request.user

        order = OrderGoods.objects.filter(order_id=order_id).order_by('create_time')
        serializer = self.get_serializer(order, many=True)
        return Response(serializer.data)


class GoodsComment(GenericAPIView):
    permission_classes = [IsAuthenticated]  # 给视图指定权限
    """
    通过UpdateAPIView修改lookip_field提交也可
    serializer_class = GoodsComments
    lookup_field = "order_id"

    def get_queryset(self):
        sku_id = self.request.data.get('sku')
        sku = SKU.objects.get(id=sku_id)
        queryset = sku.ordergoods_set.all()
        return queryset

    """
    def put(self, request, order_id):
        data = request.data
        # 开启一个事务
        with transaction.atomic():

            # 创建事务保存点
            save_point = transaction.savepoint()
            try:
                # 更改订单商品信息
                order_good = OrderGoods.objects.filter(order_id=order_id, sku_id=data.get('sku')).update(
                    comment=data.get('comment'),
                    is_commented=True,
                    is_anonymous=data.get('is_anonymous'),
                    score=data.get('score'))
                print(order_good)
                goods = OrderGoods.objects.filter(order_id=order_id)
                order = OrderInfo.objects.get(order_id=order_id)
                is_commenteds = []
                for good in goods:
                    is_commenteds.append(good.is_commented)
                if all(is_commenteds):
                    order.status = 5
                    order.save()
                sku = SKU.objects.get(id=data.get('sku'))
                # 获取查询出sku那一刻的评论
                origin_comments = sku.comments
                # 增加评价数 SKU   乐观锁
                comments = origin_comments + 1
                result = SKU.objects.filter(id=sku.id, comments=origin_comments).update(comments=comments)
            except Exception:
                # 暴力回滚,无论中间出现什么问题全部回滚
                transaction.savepoint_rollback(save_point)
                raise
            else:
                transaction.savepoint_commit(save_point)

        return Response(status=status.HTTP_200_OK)


