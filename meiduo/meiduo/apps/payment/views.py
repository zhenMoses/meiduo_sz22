from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from alipay import AliPay
from django.conf import settings
import os

from orders.models import OrderInfo


# Create your views here.
# 1.生成支付宝登录url

class PaymentView(APIView):
    """生成支付宝登录url"""
    permission_classes = [IsAuthenticated]  # 必须是登录用户才能访问此视图

    def get(self, request, order_id):
        # 获取当前登录用户
        user = request.user
        try:
            # 校验订单编号
            order = OrderInfo.objects.get(order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return Response({'message': '订单信息有误'}, status=status.HTTP_400_BAD_REQUEST)
        """
        # 支付宝
        ALIPAY_APPID = '2016091900551154'
        ALIPAY_DEBUG = True
        ALIPAY_URL = 'https://openapi.alipaydev.com/gateway.do'
        """
        # 创建alipay支付对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/app_private_key.pem'),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/alipay_public_key.pem'),
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )

        # 调用它里面的方法 生成支付宝登录url后面的 查询参数部分
        # 电脑网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 美多商城订单编号
            total_amount=str(order.total_amount),  # 一定要把总价转换成字符串类型,不然会报错
            subject='美多商城%s' % order_id,
            return_url="http://www.meiduo.site:8080/pay_success.html",  # 支付成功后的回调url
        )
        # 拼接完整 支付宝登录url
        # 沙箱环境 : 	https://openapi.alipaydev.com/gateway.do? + 查询参数部分

        # 真实环境 : 	https://openapi.alipay.com/gateway.do? + 查询参数部分  order_id=xxx&a=xxx
        alipay_url = settings.ALIPAY_URL + '?' + order_string

        return Response({'alipay_url': alipay_url})

# 2.支付成功后的验证和修改订单状态 保存订单及支付流水号
