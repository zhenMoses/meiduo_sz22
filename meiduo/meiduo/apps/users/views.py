import re
from datetime import datetime
import pickle,base64
import json
from random import randint

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework_jwt.settings import api_settings
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework_jwt.views import ObtainJSONWebToken, jwt_response_payload_handler

from carts.utils import merge_cart_cookie_to_redis
from goods.models import SKU
from goods.serializers import SKUSerializer
from meiduo_mall.utils.captcha.captcha import captcha
from meiduo_mall.utils.exceptions import logger

from celery_tasks.sms.tasks import send_sms_code
from oauth.utils import generate_save_user_token
from orders.serializers import CheckPasswordSerializer
from users import constants
from users.utils import get_user_by_account
from .models import User
from .serializers import UserSerializer, UserDetailSerializer, EmailSerializer, UserAddressSerializer, \
    AddressTitleSerializer, UserBrowseHistorySerializer


# class ImageCheckView(APIView):
#     """忘记密码之验证图片验证码"""
#     def get(self,request,username):
#
#         # 获取图片验证码的信息uuid
#         image_code_id = request.query_params.get('image_code_id')
#         # 获取前端发送的验证码信息
#         image_code = request.query_params.get('text')
#         # 判断用户是否存在
#         try:
#             user =User.objects.get(Q(mobile=username) | Q(username=username))
#         except Exception:
#             return Response({'messsage':'查询数据失败'},status=status.HTTP_404_NOT_FOUND)
#
#         if not user:
#             return Response({'message':'用户不存在'},status=status.HTTP_400_BAD_REQUEST)
#         # 手动生成token
#         jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 加载生成载荷函数
#         jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 加载生成token函数
#
#         payload = jwt_payload_handler(user)  # 生成载荷
#         token = jwt_encode_handler(payload)  # 根据载荷生成token
#
#         data ={
#             'access_token':token,
#             'mobile':user.mobile
#         }
#         # 创建redis连接对象
#         redis_conn = get_redis_connection('image')
#         # 获取redis数据库中图片验证码
#         real_image_code = redis_conn.get('image_%s' % image_code_id)
#
#         # 因为手机号是前端自己绑定,没有传送,而在短信验证码,需要传手机号,token是连接两步的唯一枢纽,所以以token为key保存手机号码
#         redis_conn.setex('token_%s' % token, constants.SMS_CODE_REDIS_EXPIRES, user.mobile)
#         # 判断是否存在图片验证码
#         if not real_image_code:
#             return Response({'message':'图片验证码过期'},status=status.HTTP_404_NOT_FOUND)
#
#         # else:
#         #     redis_conn.delete("image_%s" % image_code_id)
#
#         if image_code.lower() != real_image_code.lower().decode():
#             return Response({'message':'图片验证码错误'},status=status.HTTP_400_BAD_REQUEST)
#
#         return Response(data)
#
#
# class FindPWSMSView(APIView):
#     """忘记密码之发送短信验证码"""
#     # sms_codes /?access_token
#     def get(self,request):
#         # 获取access_token的值
#         token = request.query_params.get('access_token')
#
#         if not token:
#             return Response({'message': '缺少access_token的值'}, status=status.HTTP_400_BAD_REQUEST)
#         # 0.创建redis连接对象
#         redis_conn = get_redis_connection('image')
#         # 因为只有token是枢纽,根据token的值,查出mobile
#         mobile =redis_conn.get('token_%s' % token).decode()
#
#         # 0.创建redis连接对象
#         redis_conn = get_redis_connection('verify_codes')
#         # 1.获取此手机号是否有发送过的标记
#         flag = redis_conn.get('send_flag_%s' % mobile)
#         # 2.如果已发送就提前响应,不执行后续代码
#         if flag:  # 如果if成立说明此手机号60秒内发过短信
#             return Response({'message': '频繁发送短信'}, status=status.HTTP_400_BAD_REQUEST)
#
#         # 3生成六位随机验证码
#         smc_code = '%06d' % randint(0, 999999)
#         logger.info(smc_code)
#         # 创建redis的管道命令
#         pl = redis_conn.pipeline()
#
#         # 4把短信验证码缓存到redis  setex(key 过期时间, value)
#         pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, smc_code)
#         # 4.1 存储此手机号已发送短信标记
#         pl.setex('send_flag_%s' % mobile, constants.SMS_CODE_REDIS_SIANS, 1)
#
#         # 执行管道
#         pl.execute()
#         # 5使用容联云通讯去发送短信  send_template_sms(self, to, datas, temp_id)
#         # CCP().send_template_sms( mobile,[smc_code,constants.SMS_CODE_REDIS_EXPIRES // 60],1)
#
#         # 触发异步任务(让发短信不要阻塞主线程)
#         send_sms_code.delay(mobile, smc_code)
#         # 6响应结果
#
#
#         return Response({'message':'ok'})
#
#
#
# class SMSCheckView(APIView):
#     """重置密码之验证短信验证码"""
#     #     '/accounts/' + this.username + '/password/token/?sms_code='
#     def get(self, request, mobile):
#         smc_code = request.query_params.get('sms_code')
#
#         redis_conn = get_redis_connection('verify_codes')
#         real_smc_code = redis_conn.get('sms_%s' % mobile)
#
#         if not real_smc_code:
#             return Response({'message': '短信验证码过期'}, status=status.HTTP_404_NOT_FOUND)
#         #
#         if smc_code != real_smc_code.decode():
#             return Response({'message': '短信验证码错误'})
#         try:
#             user = User.objects.get(mobile=mobile)
#         except:
#             return Response({'message': '手机号不存在'})
#
#         jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 加载生成载荷函数
#         jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 加载生成token函数
#
#         payload = jwt_payload_handler(user)  # 生成载荷
#         token = jwt_encode_handler(payload)  # 根据载荷生成token
#
#         data = {
#             'access_token': token,
#             'user_id': user.id,
#             'username':user.username
#         }
#
#         return Response(data)
#
#
# class FindResetPWView(APIView):
#     """忘记密码之重置密码"""
#
#     def post(self,request,pk):
#         password = request.data.get('password')
#         password2 = request.data.get('password2')
#
#
#         try:
#             user = User.objects.get(id=pk)
#         except User.DoesExist:
#             return Response({'message':'用户不存在'},status=status.HTTP_404_NOT_FOUND)
#
#         if not all([password,password2]):
#             return Response({'message':'参数不全'},status=status.HTTP_400_BAD_REQUEST)
#
#         if not re.match(r'\w{8,20}$', password):
#             return Response({'message':'密码不符合规则'},status=status.HTTP_400_BAD_REQUEST)
#
#         if password !=password2:
#             raise Exception('两次密码输入不一致')
#         user.set_password(password)
#         user.save()
#         return Response({'message':'ok'},status=status.HTTP_201_CREATED)
#
#
# class ImageCodeView(APIView):
#     """忘记密码的获取图片验证码,"""
#
#     def get(self, request, image_code_id):
#         # 建立redis连接
#         mage_name, real_image_code, image_data = captcha.generate_captcha()
#
#         redis_conn = get_redis_connection('image')
#         pl = redis_conn.pipeline()
#         pl.setex("image_%s" % image_code_id, 300, real_image_code)
#         pl.execute()
#         return HttpResponse(image_data,content_type='image/jpg')

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
            raise Exception('用户不存在')
        if not user.check_password(data['old_password']):
            raise Exception('原密码错误')
        elif not re.match(r'\w{8,20}$', data['psssword']):
            return Response({'message':'密码不符合规则'},status=status.HTTP_400_BAD_REQUEST)
        elif data['password'] != data['password2']:
            raise Exception('两次密码输入不一致')
        user.set_password(data['password'])
        user.save()
        return Response({"message": 'OK'})


class UserAuthorizeView(ObtainJSONWebToken):
    """重写账号密码登录视图"""

    def post(self, request, *args, **kwargs):
        response = super(UserAuthorizeView, self).post(request, *args, **kwargs)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            merge_cart_cookie_to_redis(request, user, response)

            return response


class UserBrowseHistoryView(CreateAPIView):
    """用户浏览商品记录"""
    serializer_class = UserBrowseHistorySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """读取用户的浏览记录"""
        # 创建redis连接对象
        redis_conn = get_redis_connection('history')
        # 查询出redis中当前登录用户的浏览记录[b'1', b'2', b'3']
        sku_ids = redis_conn.lrange('history_%d' % request.user.id, 0, -1)

        # 把sku_id对应的sku模型取出来
        # skus = SKU.objects.filter(id__in=sku_ids)  # 此查询它会对数据进行排序处理
        # 查询sku列表数据
        sku_list = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            sku_list.append(sku)

        # 序列化器
        serializer = SKUSerializer(sku_list, many=True)

        return Response(serializer.data)


class AddressViewSet(CreateModelMixin, UpdateModelMixin, GenericViewSet):
    """
    用户地址新增与修改
    """
    serializer_class = UserAddressSerializer
    permissions = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    # GET /addresses/
    def list(self, request, *args, **kwargs):
        """
        用户地址列表数据
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user

        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data,
        })

    # POST /addresses/
    def create(self, request, *args, **kwargs):
        """
        保存用户地址数据
        """
        # 检查用户地址数据数目不能超过上限
        count = request.user.addresses.count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message': '保存地址数据已达到上限'}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    # delete /addresses/<pk>/
    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        """
        address = self.get_object()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    # put /addresses/pk/status/
    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        """
        设置默认地址
        """
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    # put /addresses/pk/title/
    # 需要请求体参数 title
    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """
        修改标题
        """
        address = self.get_object()
        serializer = AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class EmailVerifyView(APIView):
    """激活邮箱
        为什么要用APIView,因为只有查询get操作,没有用到序列化和反序列化
    """

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


class EmailView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmailSerializer

    def get_object(self):
        return self.request.user


# Create your views here.
# GET   /user/
# class UserDetailView(APIView):
#     """用户中心个人信息视图"""
#     # 指定权限,必须是通过认证的用户才能访问此接口(就是当前本网站的登录用户)
#     permission_classes = [IsAuthenticated]
#
#     def get_object(self,request):
#         user = request.user  # 获取本次请求的用户对象
#         serializer = UserDetailSerializer  # 指定序列化器
#         return  Response(serializer.data)


class UserDetailView(RetrieveAPIView):
    """提供用户个人信息接口"""
    permission_classes = [IsAuthenticated]  # 指定权限,必须是通过认证的用户才能访问此接口(就是当前本网站的登录用户)

    serializer_class = UserDetailSerializer  # 指定序列化器

    # queryset = User.objects.all()
    def get_object(self):  # 返回指定模型对象
        return self.request.user


# POST /users/
class UserView(CreateAPIView):
    # 指定序列化器
    serializer_class = UserSerializer


# url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
class UsernameCountView(APIView):
    """用户是否存在"""

    def get(self, request, username):
        # 查询用户是否存在
        count = User.objects.filter(username=username).count()
        # 构造响应数据
        data = {
            'username': username,
            'count': count
        }

        return Response(data)


# url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
class MobileCountView(APIView):
    """"验证手机号是否已存在"""

    def get(self, request, mobile):
        # 根据前端传来的手机号,查询这个手机号的数量,1代表已存在,0代表无
        count = User.objects.filter(mobile=mobile).count()

        data = {
            'count': count,
            'mobile': mobile
        }
        return Response(data)
