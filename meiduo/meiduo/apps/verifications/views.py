from django_redis import get_redis_connection
from rest_framework.views import APIView
from rest_framework.response import Response
from random import randint
# from celery_tasks.sms.yuntongxun import CCP
import logging
from rest_framework import status

from . import constants
from celery_tasks.sms.tasks import send_sms_code
# Create your views here.

logger=logging.getLogger('django')
class SMSCodeView(APIView):
    """发送短信视图"""

    def get(self,request,mobile):
        """
         GET /sms_codes/(?P<mobile>1[3-9]\d{9})/
        :param request:
        :param mobile:
        :return:
        """
        # 0.创建redis连接对象
        redis_conn = get_redis_connection('verify_codes')
        # 1.获取此手机号是否有发送过的标记
        flag = redis_conn.get('send_flag_%s' % mobile)
        # 2.如果已发送就提前响应,不执行后续代码
        if flag:  # 如果if成立说明此手机号60秒内发过短信
            return Response({'message': '频繁发送短信'}, status=status.HTTP_400_BAD_REQUEST)

        # 3生成六位随机验证码
        smc_code='%06d' % randint(0,999999)
        logger.info(smc_code)
        # 创建redis的管道命令
        pl = redis_conn.pipeline()

        # 4把短信验证码缓存到redis  setex(key 过期时间, value)
        pl.setex('sms_%s' % mobile,constants.SMS_CODE_REDIS_EXPIRES,smc_code)
        # 4.1 存储此手机号已发送短信标记
        pl.setex('send_flag_%s' % mobile, constants.SMS_CODE_REDIS_SIANS, 1)

        # 执行管道
        pl.execute()
        # 5使用容联云通讯去发送短信  send_template_sms(self, to, datas, temp_id)
        # CCP().send_template_sms( mobile,[smc_code,constants.SMS_CODE_REDIS_EXPIRES // 60],1)

        # 触发异步任务(让发短信不要阻塞主线程)
        send_sms_code.delay(mobile, smc_code)
        # 6响应结果
        return Response({'message':'OK'})
