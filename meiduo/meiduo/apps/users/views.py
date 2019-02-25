import re

from django.db.models import Q
from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView, ListAPIView
from rest_framework.mixins import UpdateModelMixin, CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_jwt.views import ObtainJSONWebToken

from goods.models import SKU
from goods.serializers import SKUSerializer
from meiduo.utils.captcha.captcha import captcha
from meiduo.utils.paginations import StandardResultsSetPagination
from oauth.utils import generate_save_user_token
from orders.models import OrderInfo
from users import serializers, constants
from .serializers import UserSerializer, UserDetailSerializer, UserAddressSerializer, AddressTitleSerializer, \
    UserBrowseHistorySerializer, OrderDefaultSerialzier, CheckPasswordSerializer
from .models import User
from carts.utils import merge_cart_cookie_to_redis


class SendImageAPIView(APIView):
    """生成图片验证码"""

    def get(self, request, image_code_id):
        # 1. 生成验证码
        name, text, image = captcha.generate_captcha()
        # 2.创建redis对象
        redis_conn = get_redis_connection("image")
        try:
            # 保存当前生成的图片验证码内容
            redis_conn.setex('ImageCode_' + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        except Exception as e:
            redis_conn.logger.error(e)
            return Response("保存图形验证码异常")

        # 返回响应内容
        resp = Response(content_type='text/html; charset=utf-8')

        resp.content = image

        return resp


class CheckImageAPIView(APIView):
    """校验图片验证码"""

    def get(self, request, username):
        # 1.获取参数
        # 根据获得参数username,查询用户是否存在
        try:
            user = User.objects.get(Q(mobile=username) | Q(username=username))
        except User.DoesNotExist:
            return Response({"message": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        image_code = request.query_params.get("text")
        image_code_id = request.query_params.get("image_code_id")
        if not all([image_code_id, image_code]):
            Response({"message": "参数不全"}, status=status.HTTP_400_BAD_REQUEST)
        # 2.创建redis对象
        redis_conn = get_redis_connection("image")
        real_image_code = redis_conn.get("ImageCode_" + image_code_id)
        print(real_image_code)
        # 如果能够取出来值，删除redis中缓存的内容
        if real_image_code:
            real_image_code = real_image_code.decode()
            redis_conn.delete("ImageCode_" + image_code_id)
            # 3.1 判断验证码是否存在，已过期
        if not real_image_code:
            # 验证码已过期
            return Response({"message": "参数不全"}, status=status.HTTP_400_BAD_REQUEST)
            # 4. 进行验证码内容的比对
        if image_code.lower() != real_image_code.lower():
            # 验证码输入错误
            return Response({"message": "参数不全"}, status=status.HTTP_400_BAD_REQUEST)

        access_token = generate_save_user_token(user.mobile)
        # mobile=user.mobile
        # mobile=mobile.replace(mobile[3:7], '****')
        return Response({
            "mobile": user.mobile,
            "access_token": access_token,
        })


class CheckSMSCodeAPIView(APIView):
    """校验验证码"""

    def get(self, request, mobile):
        # 1.获取参数
        sms_code = request.query_params.get("sms_code")
        # 2.创建redis对象
        redis_conn = get_redis_connection('verify_codes')
        # 3.根据获得参数username,查询用户是否存在
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            return Response({"message": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)
        """校验验证码"""
        # 数据库保存的验证码
        try:
            real_sms_code = redis_conn.get('sms_%s' % user.mobile).decode()
        # 如果验证码不存在
        except Exception:
            return Response({"message": "验证码错误"}, status=status.HTTP_400_BAD_REQUEST)
        if sms_code is None:
            return Response({"message": "短信验证码已过期"}, status=status.HTTP_404_NOT_FOUND)
        # 对用户和数据库的验证吗进行校验
        if sms_code != real_sms_code:
            return Response({"message": "验证码错误"}, status=status.HTTP_400_BAD_REQUEST)

        # 根据用户对象,生成access_token
        # from .utils import generate__user_token


        access_token = generate_save_user_token(mobile)

        return Response({
            "user_id": user.id,
            "access_token": access_token,
        })




class CheckPasswordAPIView(APIView):
    """重置密码"""

    def post(self, request, pk):
        # 1.获取user实例对象
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({"message": "用户不存在"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CheckPasswordSerializer(instance=user, data=request.data, context={"user": user})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status.HTTP_200_OK)


class PasswordUpdateView(APIView):
    """修改密码"""
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        data = request.data

        try:
            user = User.objects.get(id=pk)
        except User.DoesExist:
            return Response({'message': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        if not user.check_password(data['old_password']):
            return Response({'message': '原密码错误'}, status=status.HTTP_400_BAD_REQUEST)
        elif not re.match(r'\w{8,20}$', data['password']):
            return Response({'message': '密码不符合规则'}, status=status.HTTP_400_BAD_REQUEST)
        elif data['password'] != data['password2']:
            raise Exception('两次密码输入不一致')
        user.set_password(data['password'])
        user.save()
        return Response({"message": 'OK'})





# Create your views here.

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


class UserDetailView(RetrieveAPIView):
    """提供用户个人信息接口"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class EmailView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.EmailSerializer

    def get_object(self, *args, **kwargs):
        return self.request.user


class EmailVerifyView(APIView):
    """激活邮箱"""

    def get(self, request):
        # 1.获取钱token查询参数
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


class AddressViewSet(UpdateModelMixin, CreateModelMixin, GenericViewSet):
    """用户收货地址"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserAddressSerializer


    def create(self, request, *args, **kwargs):
        """新增收货地址"""
        # 判断用户的收货地址数量是否上限
        # address_count = request.user.addresses.count()
        address_count = request.user.addresses.count()
        if address_count > 20:
            return Response({'message': '收货地址数量上限'},
                            status=status.HTTP_400_BAD_REQUEST)
        # 创建序列化器给data参数传值(反序列化)
        # serializer = UserAddressSerializer(data=request.data, context={'request': request})
        # # 调用序列化器的is_valid方法
        # serializer.is_valid(raise_exception=True)
        # # 调用序列化器的save
        # serializer.save()
        # # 响应
        # return Response(serializer.data, status=status.HTTP_201_CREATED)
        return super(AddressViewSet, self).create(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    # GET /addresses/
    def list(self, request, *args, **kwargs):
        """用户地址列表数据"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': 20,
            'addresses': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        """处理删除"""
        address = self.get_object()
        address.is_deleted = True
        address.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # put /addresses/pk/status/
    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        """设置默认地址"""
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    # put /addresses/pk/title/
    # 需要请求体参数 title
    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """修改标题"""
        address = self.get_object()
        serializer = AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# Create your views here.
# POST/GET  /browse_histories/
class UserBrowseHistoryView(CreateAPIView):
    """用户浏览记录"""


    # 指定权限
    permission_classes = [IsAuthenticated]
    # 指定序列化器（校验）
    serializer_class = UserBrowseHistorySerializer

    def get(self, request):
        """读取用户浏览记录"""
        # 创建redis连接对象
        redis_conn = get_redis_connection('history')
        # 查询出redis中当前登录用户的浏览记录[b'1', b'2', b'3']
        sku_ids = redis_conn.lrange('history_%d' % request.user.id, 0, -1)

        # 把sku_id对应的sku模型取出来
        # skus = SKU.objects.filter(id__in=sku_ids) #此查询它会对数据进行排序处理
        # 查询sku列表数据
        sku_list = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            sku_list.append(sku)

        # 序列化器
        serializer = SKUSerializer(sku_list, many=True)
        return Response(serializer.data)


class UserAuthorizeView(ObtainJSONWebToken):
    """重写账户密码登录视图"""
    def post(self, request, *args, **kwargs):
        response = super(UserAuthorizeView, self).post(request, *args, **kwargs)
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            merge_cart_cookie_to_redis(request, user, response)

        return response


#  r'^order/?page=xxx&page_size=xxx'
class OrderDefaultView(ListAPIView):
    """订单列表展示"""
    permission_classes = [IsAuthenticated]
    serializer_class = OrderDefaultSerialzier
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        queryset = OrderInfo.objects.filter(user_id=user.id).order_by('-create_time')
        # seroalzier = OrderDefaultSerialzier(seroalzier, many=True)
        # return Response({'results': seroalzier.data})
        return queryset