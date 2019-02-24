from QQLoginTool.QQtool import OAuthQQ
from rest_framework_jwt.settings import api_settings
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
# Create your views here.
import logging

from oauth.models import QQAuthUser
from oauth.utils import generate_save_user_token
from oauth.serializers import QQAuthUserSerializer
from carts.utils import merge_cart_cookie_to_redis

logger = logging.getLogger('django')




class QQAuthUserView(APIView):
    """扫码成功后回调处理"""

    def get(self, request):
        """提取code请求参数"""
        code = request.query_params.get('code')
        if not code:
            return Response({'message': '缺少code的值'}, status=status.HTTP_400_BAD_REQUEST)
        # 1.1 创建qq登录工具对象
        oauthqq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                          client_secret=settings.QQ_CLIENT_SECRET,
                          redirect_uri=settings.QQ_REDIRECT_URI)

        try:
            # 2.通过code向QQ服务器请求获取access_token
            access_token = oauthqq.get_access_token(code)
            # 3.通过access_token向QQ服务器请求获取openid
            openid = oauthqq.get_open_id(access_token)
        except Exception as e:
            logger.info(e)
            return Response({'message': 'QQ服务器异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 4.查询openid是否绑定过美多商城中的用户
        try:
            qqauth_model = QQAuthUser.objects.get(openid=openid)
        except QQAuthUser.DoesNotExist:
            # 如果qqauth_model异常,说明用户没有进行过QQ登录,
            # 如果openid没有绑定过美多商城中的用户
            # 把openid进行加密安全处理,再响应给浏览器,让它先帮我们保存一会

            openid_save = generate_save_user_token(openid)
            return Response({'access_token': openid_save})

        else:
            # 如果openid已经绑定过美多商城中的用户(生成jwt token直接让它登录成功)
            # 手动生成token
            # QQ登录的状态保持
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 加载生成载荷函数
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 加载生成token函数

            user = qqauth_model.user  # 通过第三方QQ的数据的用户获取user(user是外键,可以得到User)
            payload = jwt_payload_handler(user)  # 生成载荷
            token = jwt_encode_handler(payload)  # 根据载荷生成token

            # 返回值
            response = Response({
                'token': token,
                'username': user.username,
                'user_id': user.id,
            })

            # 做cookie购物车合并到redis操作
            merge_cart_cookie_to_redis(request, user, response)

            return response

    def post(self, request):
        """openid绑定到用户"""

        # 创建序列化器对象,进行反序列化

        serializer = QQAuthUserSerializer(data=request.data)

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

        # 做cookie购物车合并到redis操作
        merge_cart_cookie_to_redis(request, user, response)

        return response


class QQAuthURLView(APIView):
    """生成QQ扫码url"""

    def get(self, request):
        # 1.获取next(从那里去到login界面)参数路径
        next = request.query_params.get('next')
        if not next:  # 如果没有指定来源将来登录成功就回到首页
            next = '/'

        """
               QQ_CLIENT_ID = '101514053'
               QQ_CLIENT_SECRET = '1075e75648566262ea35afa688073012'
               QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'
               oauthqq = OAuthQQ(client_id='101514053',
                         client_secret='1075e75648566262ea35afa688073012',
                         redirect_uri='http://www.meiduo.site:8080/oauth_callback.html',
                         state=next)
        """
        # 2.创建QQ登录sdk 的对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        # 3.调用它里面的get_qq_url方法来拿到拼接好的扫码链接
        login_url = oauth.get_qq_url()

        # 4.把扫码url响应给前端
        return Response({'login_url': login_url})


