"""xxx"""

from django.shortcuts import render
from rest_framework.views import APIView


# Create your views here.

class CartView(APIView):
    """购物车视图"""

    def perform_authentication(self, request):
        """禁用认证/延后认证"""
        pass

    def post(self, request):
        """添加购物车"""
        try:
            user = request.user  # 获取登录用户  首次获取还会做认证
            # 如果代码能继续向下走说明是登录用户存储购物车数据到redis

        except:
            # 未登录存储到cookie
            pass

    def get(self, request):
        """查询购物车"""
        pass

    def put(self, request):
        """修改购物车"""
        pass

    def delete(self, request):
        """删除购物车"""
        pass
