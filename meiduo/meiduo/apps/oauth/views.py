from django.shortcuts import render
from rest_framework.views import APIView
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from rest_framework.response import Response


# Create your views here.
class QQAuthURLView(APIView):
    """生成QQ扫码url"""

    def get(self, request):
        # 1.获取next(从那里去到login界面)参数路径
        next = request.query_params.get('next')
        if not next:  # 如果没有指定来源将来登录成功就回到首页
            next = '/'

        # QQ登录参数
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
        oauthqq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                          client_secret=settings.QQ_CLIENT_SECRET,
                          redirect_uri=settings.QQ_REDIRECT_URI,
                          state=next)
        # 3.调用它里面的get_qq_url方法来拿到拼接好的扫码链接
        login_url = oauthqq.get_qq_url()


        # 4.把扫码url响应给前端
        return Response({'login_url': login_url})