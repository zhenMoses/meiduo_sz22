from _decimal import Decimal

from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_redis import get_redis_connection

from goods.models import SKU
from meiduo_mall.utils.paginations import StandardResultsSetPagination
from orders.models import OrderInfo, OrderGoods
from orders.serializers import OrderSettlementSerializer, SaveOrderSerializer, UnCommenOrdertSerialzier


class OrderSettlementView(APIView):
    """订单结算"""
    permission_classes = [IsAuthenticated]

    def get(self,request):
        """获取购物车信息"""
        user =request.user
        # 从购物车中获取用户勾选要结算的商品信息
        # 创建redis连接对象
        redis_conn = get_redis_connection('cart')

        # 获取hash值
        cart_dict = redis_conn.hgetall('cart_%d' % user.id)
        # 获取是否勾选的值

        cart_selected = redis_conn.smembers('selected_%s' % user.id)

        cart = {}
        # 遍历选中的商品
        for sku_id in cart_selected:
            cart[int(sku_id)] = int(cart_dict[sku_id])
        # 获取商品信息
        skus = SKU.objects.filter(id__in=cart.keys())

        # 对商品信息进行遍历
        for sku in skus:
            # sku_id 是商品id,通过sku.id 在cart 中找到所对应的count
            sku.count = cart[sku.id]
        # 运费
        freight = Decimal('10.00')
        # data = {'freight': freight, 'skus': skus}
        #  serializer = OrderSettlementSerializer(data)

        # 创建序列化器时 给instance参数可以传递(模型/查询集(many=True) /字典)
        serializer = OrderSettlementSerializer({'freight': freight, 'skus': skus})

        return Response(serializer.data)


class SaveOrderView(CreateAPIView):
    """保存订单"""
    # 指定权限
    permission_classes = [IsAuthenticated]
    # 指定序列化器
    serializer_class = SaveOrderSerializer


#
# class UnCommenOrdertView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self,request,order_id):
#         user = request.data.get('user')
#         # status=OrderInfo.ORDER_STATUS_CHOICES['UNCOMMENT']
#         serializer=OrderInfo.objects.filter(order_id=order_id,user=user).all()
#         serializer=UnCommenOrdertSerialzier(serializer,many=True)
#         return Response(serializer.data)


        #
        # try:
        #     orders =OrderInfo.objects.filter(order_id=order_id,user=user,status=status).all()
        # except OrderInfo.DoesExist:
        #     return Response({'message':'数据库查询失败'},status=status.HTTP_400_BAD_REQUEST)
        #


        # user=request.user
        #
        # queryset =OrderInfo.objects.filter(order_id=order_id,user=user).all()
        # return queryset
        # skus_list=[]
        # for sku in orders:
        #     skus_list[sku] =
        # # for sku in orders.sku_id:
        # #     sku = SKU.objects.get(sku=sku)
        # #     skus_list.append(sku)




