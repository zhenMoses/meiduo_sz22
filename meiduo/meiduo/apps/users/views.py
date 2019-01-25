from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin

from .serializers import UserSerializer, UserDetailSerializer, EmailSerializer
from .models import User


# Create your views here.
class AddressViewSet(GenericViewSet):
    """用户收货地址"""
    permission_classes = [IsAuthenticated]

    # serializer_class = '序列化器'

    def create(self, request):
        """新增收货地址"""
        # 判断用户的收货地址数量是否上限
        # 创建序列化器给data参数传值(反序列化)
        # 调用序列化器的is_valid方法
        # 调用序列化器的save
        # 响应





class EmailVerifyView(APIView):
    """激活邮箱"""
    def get(self, request):

        # 1.获取前token查询参数
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)

        # 对token解密并返回查询到的user
        user = User.check_verify_email_token(token)

        if not user:
            return Response({'message': '无效token'}, status=status.HTTP_400_BAD_REQUEST)

        # 修改user的email_active字段
        user.email_active = True
        user.save()

        return Response({'message': 'ok'})





# PUT  /email/
class EmailView(UpdateAPIView):
    """保存邮箱"""
    permission_classes = [IsAuthenticated]
    # 指定序列化器
    serializer_class = EmailSerializer

    def get_object(self):
        return self.request.user




"""
# GET   /user/
class UserDetailView(APIView):
    # 提供用户个人信息接口
    # 指定权限,必须是通过认证的用户才能访问此接口(就是当前本网站的登录用户)
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        user = request.user  # 获取本次请求的用户对象
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)
"""

class UserDetailView(RetrieveAPIView):
    """提供用户个人信息接口"""
    permission_classes = [IsAuthenticated]  # 指定权限,必须是通过认证的用户才能访问此接口(就是当前本网站的登录用户)

    serializer_class = UserDetailSerializer  # 指定序列化器

    # queryset = User.objects.all()
    def get_object(self):  # 返回指定模型对象
        return self.request.user


# POST /users/
class UserView(CreateAPIView):
    """用户注册"""
    # 指定序列化器
    serializer_class = UserSerializer


# url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
class UsernameCountView(APIView):
    """验证用户名是否已存在"""

    def get(self, request, username):
        # 查询用户名是否已存在
        count = User.objects.filter(username=username).count()

        # 构建响应数据
        data = {
            'count': count,
            'username': username
        }
        return Response(data)


# url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
class MobileCountView(APIView):
    """验证手机号是否已存在"""

    def get(self, request, mobile):
        # 查询手机号数量
        count = User.objects.filter(mobile=mobile).count()

        data = {
            'count': count,
            'mobile': mobile
        }
        return Response(data)
