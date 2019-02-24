from django.conf.urls import url
from . import views

from rest_framework_jwt.views import obtain_jwt_token
from  rest_framework.routers import DefaultRouter

urlpatterns=[
    # 注册路由
    url(r'^users/$',views.UserView.as_view()),
    # 修改密码
    url(r'^users/(?P<pk>\d)/password/$', views.PasswordUpdateView.as_view()),

    # 判断用户名是否已存在
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),


    # 判断手机号是否已存在
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),

    # JWT登录
    # url(r'^authorizations/$', obtain_jwt_token),
    url(r'^authorizations/$', views.UserAuthorizeView.as_view()),
    # 获取用户个信信息
    url(r'^user/$',views.UserDetailView.as_view()),
    # 保存邮箱
    url(r'^email/$',views.EmailView.as_view()),

    # 激活邮箱
    url(r'^emails/verification/$',views.EmailVerifyView.as_view()),

    # 浏览记录
    url(r'^browse_histories/$', views.UserBrowseHistoryView.as_view()),


    # 以下5个路由是忘记密码功能的
    #生成图片验证码
    url(r'^image_codes/(?P<image_code_id>[\w-]+)/$',views.ImageCodeView.as_view()),

    # 判断用户是否存在(如果存在,可以修改,否则去注册)
    url(r'^accounts/(?P<username>.*)/sms/token/$', views.ImageCheckView.as_view()),
    #手机号发送短信验证码
    url(r'^sms_codes/$', views.FindPWSMSView.as_view()),
    # 验证短信验证路由
    url(r'accounts/(?P<mobile>.*)/password/token/$',views.SMSCheckView.as_view()),

    url(r'user/(?P<pk>\d+)/password/$',views.FindResetPWView.as_view())

]

router = DefaultRouter()
router.register(r'addresses', views.AddressViewSet, base_name='addresses')
urlpatterns += router.urls