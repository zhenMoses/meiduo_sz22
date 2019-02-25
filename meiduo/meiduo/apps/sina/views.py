from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from meiduo.utils.exceptions import logger
from oauth.utils import generate_save_user_token
from sina.models import SinaAuthUser
from sina.serializers import SinaWeiboUserSerializer
from .OauthWeiBo import WeiboSDK


class SinaWeiBoUserView(APIView):
    """扫码成功后回调处理"""

    def get(self, request):
        """提取code请求参数"""
        code = request.query_params.get('code')
        if not code:
            return Response({'message': '缺少code的值'}, status=status.HTTP_400_BAD_REQUEST)
        sinaweibo = WeiboSDK(client_id=settings.WEIBO_CLIENT_ID, client_secret=settings.WEIBO_CLIENT_SECRET,
                        redirect_uri=settings.WEIBO_REDIRECT_URI)
        try:
            access_token =sinaweibo.get_access_token(code)

        except Exception as e:
            logger.info(e)
            return Response({'message': '微博服务器异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            sinaweibo_model = SinaAuthUser.objects.get(access_token=access_token)
        except SinaAuthUser.DoesNotExist:
            access_token = generate_save_user_token(access_token)
            return Response({'access_token': access_token})
        else:
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 加载生成载荷函数
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 加载生成token函数

            user = sinaweibo_model.user  # 通过第三方QQ的数据的用户获取user(user是外键,可以得到User)
            payload = jwt_payload_handler(user)  # 生成载荷
            token = jwt_encode_handler(payload)  # 根据载荷生成token

            # 返回值
            response = Response({
                'token': token,
                'username': user.username,
                'user_id': user.id,
            })
            # # 做cookie购物车合并到redis操作
            # merge_cart_cookie_to_redis(request, user, response)
            return response

    def post(self, request):
        """access_token绑定到用户"""

        # 创建序列化器对象,进行反序列化

        serializer = SinaWeiboUserSerializer(data=request.data)

        # 开启校验
        serializer.is_valid(raise_exception=True)
        # 保存校验结果，并接收
        user = serializer.save()

        # 手动生成jwt Token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 加载生成载荷函数
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 加载生成token函数
        # 获取user对象

        payload = jwt_payload_handler(user)  # 生成载荷
        token = jwt_encode_handler(payload)  # 根据载荷生成token

        response = Response({
            'token': token,
            'username': user.username,
            'user_id': user.id
        })

        # # 做cookie购物车合并到redis操作
        # merge_cart_cookie_to_redis(request, user, response)

        return response


class  WeiboAuthURLView(APIView):
    """生成微博扫码url"""


    def get(self, request):
        next =request.query_params.get('next')
        if not next:
            next = '/'

        sina = WeiboSDK(client_id=settings.WEIBO_CLIENT_ID, client_secret=settings.WEIBO_CLIENT_SECRET,
                         redirect_uri=settings.WEIBO_REDIRECT_URI, state=next)
        login_url = sina.get_weibo_login_url()
        # 4.把扫码url响应给前端
        return Response({'login_url': login_url})