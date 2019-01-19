from django.shortcuts import render
from rest_framework.generics import CreateAPIView

from .serializers import UserSerializer
# Create your views here.

# POST /users/
class UserView(CreateAPIView):
    """用户注册"""
    # 指定序列化器
    serializer_class = UserSerializer