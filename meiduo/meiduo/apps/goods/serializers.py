from drf_haystack.serializers import HaystackSerializer
from rest_framework import serializers

from goods.search_indexes import SKUIndex
from orders.models import OrderGoods
from .models import SKU

class SKUSerializer(serializers.ModelSerializer):
    """商品列表界面"""
    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'default_image_url', 'comments']

class SKUCommentsSerializer(serializers.ModelSerializer):
    """商品评论界面"""
    username = serializers.CharField(label='用户名')
    class Meta:
        model = OrderGoods
        fields = ['comment', 'is_anonymous', 'score', 'username', 'is_anonymous']


class SKUIndexSerializer(HaystackSerializer):
    """
    SKU索引结果数据序列化器
    """
    object = SKUSerializer(read_only=True)

    class Meta:
        index_classes = [SKUIndex]
        fields = ('text', 'object')
