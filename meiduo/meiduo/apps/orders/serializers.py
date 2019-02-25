# from datetime import timezone
# from time import timezone
from django.utils import timezone
from rest_framework import serializers
from decimal import Decimal
from django_redis import get_redis_connection
from django.db import transaction

from goods.models import SKU
from oauth.utils import check_save_user_token
from users.models import User
from .models import OrderInfo, OrderGoods

class SaveOrderSerializer(serializers.ModelSerializer):
    """保存订单序列化器"""

    class Meta:
        model = OrderInfo
        fields = ['order_id', 'pay_method', 'address']
        # order_id 只做输出, pay_method/address只做输入
        read_only_fields = ['order_id']
        extra_kwargs = {
            'address': {
                'write_only': True,
                'required': True,
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }
        }

    def create(self, validated_data):
        """重写序列化器的create方法进行存储订单表/订单商品"""
        # 订单基本信息表 订单商品表  sku   spu 四个表要么一起成功 要么一起失败

        # 获取当前保存订单时需要的信息
        # 获取user对象
        user = self.context['request'].user
        # 生成订单编号 当前时间 + user_id  20190215100800000000001
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + "%09d" % user.id
        # 获取用户选择的收货地址
        address = validated_data.get('address')
        # 获取支付方式
        pay_method = validated_data.get('pay_method')

        # 订单状态: 如果用户选择的是货到付款, 订单应该是待发货  如果用户选择支付宝支付,订单应该是待支付
        # status = '待支付'  if 如果用户选择的支付方式 == 支付宝支付 else '待发货'
        status = (OrderInfo.ORDER_STATUS_ENUM['UNPAID']
                  if OrderInfo.PAY_METHODS_ENUM['ALIPAY'] == pay_method
                  else OrderInfo.ORDER_STATUS_ENUM['UNSEND'])

        # 开启一个事务
        with transaction.atomic():

            # 创建事务保存点
            save_point = transaction.savepoint()
            try:

                # 保存订单基本信息 OrderInfo（一）
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal('0.00'),
                    freight=Decimal('10.00'),
                    pay_method=pay_method,
                    status=status
                )

                # 从redis读取购物车中被勾选的商品信息
                redis_conn = get_redis_connection('cart')
                # {b'16: 1, b'1': 1}
                cart_redis_dict = redis_conn.hgetall('cart_%d' % user.id)
                # {b'16'}
                cart_selected_ids = redis_conn.smembers('selected_%d' % user.id)
                # 把要购买的商品id和count重新包到一个字典
                cart_selected_dict = {}  # {16: 6}
                for sku_id_bytes in cart_selected_ids:
                    cart_selected_dict[int(sku_id_bytes)] = int(cart_redis_dict[sku_id_bytes])

                # 遍历购物车中被勾选的商品信息
                # skus = SKU.objects.filter(id__in=cart_selected_dict.keys())  # 此处不要这样一下全取出,因为并发时会有缓存问题
                for sku_id in cart_selected_dict:

                    while True:
                        # 获取sku对象
                        sku = SKU.objects.get(id=sku_id)
                        # 获取当前sku_id商品要购买的数量
                        sku_count = cart_selected_dict[sku_id]



                        # 获取查询出sku那一刻库存和销量
                        origin_stock = sku.stock
                        origin_sales = sku.sales

                        # 判断库存 
                        if sku_count > origin_stock:
                            raise serializers.ValidationError('库存不足')

                        # import time
                        # time.sleep(5)

                        # 计算新库存和销量
                        new_stock = origin_stock - sku_count
                        new_sales = origin_sales + sku_count

                        # 减少库存，增加销量 SKU   乐观锁
                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock,sales=new_sales)

                        if result == 0:
                            continue  # 跳出本次循环进入下一次
                        # sku.stock -= sku_count
                        # sku.sales += sku_count
                        # sku.save()

                        # 修改SPU销量
                        spu = sku.goods
                        spu.sales += sku_count
                        spu.save()

                        # 保存订单商品信息 OrderGoods（多）
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku_count,
                            price=sku.price
                        )

                        # 累加计算总数量和总价
                        order.total_count = order.total_count + sku_count
                        # 16   100 * 2   1  200 * 2
                        order.total_amount = order.total_amount + (sku.price * sku_count)

                        break  # 跳出无限循环,继续对下一个sku_id进行下单
                # 最后加入邮费和保存订单信息(只累加一次运费)
                order.total_amount += order.freight
                print(order.total_amount)
                order.save()
            except Exception:
                # 暴力回滚,无论中间出现什么问题全部回滚
                transaction.savepoint_rollback(save_point)
                raise
            else:
                transaction.savepoint_commit(save_point)  # 如果中间没有出现异常提交事件

        # 清除购物车中已结算的商品
        pl = redis_conn.pipeline()
        pl.hdel('cart_%d' % user.id, *cart_selected_ids)
        pl.srem('selected_%d' % user.id, *cart_selected_ids)
        pl.execute()

        return order



class CartSKUSerializer(serializers.ModelSerializer):
    """
    购物车商品数据序列化器
    """
    count = serializers.IntegerField(label='数量')

    class Meta:
        model = SKU
        fields = ('id', 'name', 'default_image_url', 'price', 'count')



class OrderSettlementSerializer(serializers.Serializer):
    """
    订单结算数据序列化器
    """
    # float 1.23 ==> 123 * 10 ^ -2  --> 1.299999999
    # Decimal  1.23    1    23
    # max_digits 一共多少位；decimal_places：小数点保留几位
    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    skus = CartSKUSerializer(many=True)




class CommentSerialzier(serializers.ModelSerializer):
    class Meta:
        model=OrderGoods
        fields = ['comment','score','is_anonymous','is_commented']
        extra_kwargs={
            'comment':{
                'min_length': 5,
                'required': True,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',

                }
            },
        }

class CheckPasswordSerializer(serializers.ModelSerializer):
    """重置密码序列化器"""
    password2 = serializers.CharField(label="确认密码", write_only=True)
    access_token = serializers.CharField(label='操作凭证', write_only=True)

    class Meta:
        model = User  # 指定序列化器映射的模块
        fields = ["id", "password", "password2", "access_token"]  # 指明为模型类的哪些字段生成

    def validate(self, attrs):
        #  校验密码
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError("两次密码不一致")
        # 获取用户对象模型
        user = self.context["user"]
        # 检验token是否正确

        access_token = attrs.get("access_token")
        mobile = check_save_user_token(access_token)
        # 判断用户的手机与当前手机是否相等
        if mobile != user.mobile:
            raise serializers.ValidationError({"message":"用户与绑定的手机不一致"})


        return attrs

    def update(self, instance, validated_data):
        # 调用django的认证系统加密密码
        instance.set_password(validated_data['password'])
        instance.save()

        return instance


