from django_redis import get_redis_connection
from rest_framework import serializers

from oauth.utils import check_save_user_token
from sina.models import SinaAuthUser
from users.models import User


class SinaWeiboUserSerializer(serializers.Serializer):
    """绑定第三方微博登录用户的序列化器"""
    access_token=serializers.CharField(label='通行令牌')
    mobile=serializers.RegexField(label='手机号',regex=r'^1[3-9]\d{9}$')
    password=serializers.CharField(label='登录密码',min_length=8,max_length=20)
    sms_code = serializers.CharField(label='短信验证码')

    def validate(self, attrs):  # 使用validate进行联合验证
        # 获取access_token
        access_token = attrs.get('access_token')  # 获取加密的openid
        access_token = check_save_user_token(access_token)
        if not access_token:
            raise serializers.ValidationError('令牌已过期')
        attrs['access_token'] = access_token  # 把解密后的openid保存到反序列化的大字典中以备后期绑定用户时使用
        # 校验短信验证是否正确
        redis_conn = get_redis_connection('verify_codes')

        # 验证手机号是否存在
        mobile = attrs.get('mobile')
        real_sms_code = redis_conn.get('sms_%s' % mobile)

        # 获取前端传过来的验证码
        sms_code = attrs.get('sms_code')

        if real_sms_code.decode() != sms_code:  # 注意redis中取出来的验证码是bytes类型注意类型处理
            raise serializers.ValidationError('短信验证码输入错误')

        try:
            # 判断手机号是已存在用户的还是新用户
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 如果出现异常说明是新用户
            pass
        else:
            # 表示此手机号是已注册过的用户
            if not user.check_password(attrs.get('password')):
                raise serializers.ValidationError('密码错误')
            else:
                attrs['user'] = user

        return attrs

    def create(self, validated_data):
        """把openid和user进行绑定"""
        user = validated_data.get('user')
        if not user:
            user = User(
                username=validated_data.get('mobile'),
                password=validated_data.get('password'),
                mobile=validated_data.get('mobile')

            )
            user.set_password(validated_data.get('password'))  # 对密码进行加密
            user.save()
        # 让user和openid绑定
        SinaAuthUser.objects.create(
            user=user,
            access_token=validated_data.get('access_token')
        )

        return user
