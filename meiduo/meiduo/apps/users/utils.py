import re

from django.contrib.auth.backends import ModelBackend

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """重写jwt登录认证方法的响应体"""
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


def get_user_by_account(account):
    """通过传入手机号或用户名动态查找user"""

    # 判断account是不是手机号
    if re.match(r'1[3-9]\d{9}', account):
        # 表示是手机号登录
        try:
            user = User.objects.get(mobile=account)
        except User.DoesNotExist:
            return None

    else:
        # 用户名登录
        try:
            user = User.objects.get(username=account)
        except User.DoesNotExist:
            return None
    return user


# def get_account(account):
#     try:
#         if re.match(r'^1[3-9]{9}\d$',account):
#             user=User.objects.get(mobile=account)
#         else:
#             user=User.objects.get(username=account)
#     except User.DoesNotExist:
#
#         return None
#     else:
#         return user

class UsernameMobileAuthBackend(ModelBackend):
    """自定义django认证后端"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        :重写认证方式,使用多账号登录
        :param request:   本次登录请求对象
        :param username: 用户名/手机号
        :param password: 密码
        :return: 要么返回查到的user/None
        """
        # 1.通过传入的username 获取到user对象(通过手机号或用户名动态查询user)
        user = get_user_by_account(username)
        # 2.判断user的密码
        if user and user.check_password(password):
            return user
        else:
            # 3. 返回user/None
            return None
