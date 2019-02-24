from rest_framework import serializers
from drf_haystack.serializers import HaystackSerializer


from goods.models import SKU
from orders.models import OrderInfo, OrderGoods
from .search_indexes import SKUIndex






class SKUSerializer(serializers.ModelSerializer):
    """商品列表界面"""

    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'default_image_url', 'comments']




# class SKUSerializer(serializers.ModelSerializer):
#     """
#     SKU序列化器
#     """
#     class Meta:
#         model = SKU
#         fields = ('id', 'name', 'price', 'default_image_url', 'comments')

class SKUIndexSerializer(HaystackSerializer):
    """
    SKU索引结果数据序列化器
    """
    object = SKUSerializer(read_only=True)

    class Meta:
        index_classes = [SKUIndex]
        fields = ('text', 'object')



class OrderGoodSerializer(serializers.ModelSerializer):

    sku=SKUSerializer()
    class Meta:
        model = OrderGoods
        fields =['count','sku','price']


class OrderDefaultSerialzier(serializers.ModelSerializer):
    """"""
    skus=OrderGoodSerializer(many=True)
    class Meta:
        model=OrderInfo
        fields=['create_time','order_id','total_amount','freight','pay_method','status','skus']
        # extra_kwargs={
        #     'create_time': {'time':'%Y%m%d%H%M%S'},
        # }
