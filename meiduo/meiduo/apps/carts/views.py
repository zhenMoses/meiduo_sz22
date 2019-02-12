from django.shortcuts import render
from rest_framework.views import APIView
import pickle, base64
from rest_framework.response import Response
from rest_framework import status
from django_redis import get_redis_connection

from .serializers import CartSerializer


# Create your views here.

class CartView(APIView):
    """购物车视图"""

    def perform_authentication(self, request):
        """禁用认证/延后认证"""
        pass

    def post(self, request):
        """添加购物车"""
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')
        # 创建响应对象
        response = Response(serializer.data, status=status.HTTP_201_CREATED)
        try:
            user = request.user  # 获取登录用户  首次获取还会做认证
            # 如果代码能继续向下走说明是登录用户存储购物车数据到redis
            """
            cart_user_id: {sku_id_16: 1}   hash
        
            hincrby(cart_1, sku_id_16, 2)  # 如果sku_id,已存在,直接会做增量计算
            
            selected_user_id :{sku_id}  set
            """
            # 创建redis连接对象
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            pl.hincrby('cart_%d' % user.id, sku_id, count)
            if selected:  # 判断当前商品是否勾选, 把勾选的商品sku_id添加到set集合中
                pl.sadd('selected_%d' % user.id, sku_id)
            pl.execute()

        except:
            # 未登录存储到cookie

            """
            {
                “sku_id_1”: {
                            “selected”:  True,
                            “count”: 1
                            },
                “sku_id_2”: {
                            “selected”:  True,
                            “count": 1
			                }
            }
            """
            # 获取cookie中的购物车数据
            cart_cookie = request.COOKIES.get('carts')


            # 判断是否有购物车数据
            if cart_cookie:

                # 把字符串转python中的字典
                # 把字符串转换成bytes类型字符串
                cart_cookie_bytes = cart_cookie.encode()
                # 把bytes类型字符串转换成bytes类型ascii码
                cart_ascii_bytes = base64.b64decode(cart_cookie_bytes)
                # 把bytes类型ascii码转成python中的字典
                cart_dict = pickle.loads(cart_ascii_bytes)
            else:  # 之前没有cookie购物车数据
                cart_dict = {}


            # 判断本次添加的商品是否在购物车中已存在,如果已存要做增量计算
            if sku_id in cart_dict:
                origin_count = cart_dict[sku_id]['count']
                # count = origin_count + count
                count += origin_count

            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 把python字典转换成字符串
            cart_ascii_bytes = pickle.dumps(cart_dict)
            cart_cookie_bytes = base64.b64encode(cart_ascii_bytes)
            cart_str = cart_cookie_bytes.decode()


            response.set_cookie('carts', cart_str)


        return response

    def get(self, request):
        """查询购物车"""
        pass

    def put(self, request):
        """修改购物车"""
        pass

    def delete(self, request):
        """删除购物车"""
        pass
