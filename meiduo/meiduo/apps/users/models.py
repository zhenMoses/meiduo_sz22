from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from django.conf import settings
# Create your models here.


class User(AbstractUser):
    """自定义用户模型"""
    mobile = models.CharField(verbose_name='手机号', max_length=11, unique=True)
    email_active = models.BooleanField(verbose_name='邮箱状态', default=False)

    class Meta:
        db_table = 'tb_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


    def generate_verify_email_url(self):
        """生成激活url"""
        # 1.创建加密的序列化器对象
        serializer = Serializer(settings.SECRET_KEY, 24 * 60 * 60)
        # 2. 包装一个要加密的字典数据
        data = {'user_id': self.id, 'email': self.email}
        # 3. 调用dumps方法加密
        token = serializer.dumps(data).decode()

        # 4. 拼接好verify_url并响应
        return 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token

    @staticmethod
    def check_verify_email_token(token):
        """token解密及查询user"""
        # 1.创建加密的序列化器对象
        serializer = Serializer(settings.SECRET_KEY, 24 * 60 * 60)
        # 2. 调用loads方法对token解密
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            # 3. 取出user_id和 email 然后用这两个字段查到唯一的那个用户
            user_id = data.get('user_id')
            email = data.get('email')
            try:
                user = User.objects.get(id=user_id, email=email)
            except User.DoesNotExist:
                return None
            else:
                return user
