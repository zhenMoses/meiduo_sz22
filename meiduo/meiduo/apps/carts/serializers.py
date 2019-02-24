from rest_framework import serializers

from goods.models import SKU


class CartSerializer(serializers.Serializer):
    """
    添加/修改购物车数据序列化器(对应post/put方法)
    """
    sku_id = serializers.IntegerField(label='sku id ', min_value=1)
    count = serializers.IntegerField(label='数量', min_value=1)
    selected = serializers.BooleanField(label='是否勾选', default=True)

    def validate_sku_id(self, value):

        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('sku_id不存在')

        return value


class CartSKUSerializer(serializers.ModelSerializer):
    """获取购物车商品数据序列化器(对应get方法)"""
    count = serializers.IntegerField(label='数量')
    selected = serializers.BooleanField(label='是否勾选')

    class Meta:
        model = SKU
        fields  = ['id','name','price','count','default_image_url','selected']


class CartDeleteSerializer(serializers.Serializer):
    """删除购车序列化器(对应delete方法)"""
    sku_id = serializers.IntegerField(label='商品id',min_value=1)

    def validate_sku_id(self, value):

        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('sku_id不存在')

        return value



class CartSelectedSerializer(serializers.Serializer):
    """全选序列化器"""
    selected = serializers.BooleanField(label='全选 勾选')

