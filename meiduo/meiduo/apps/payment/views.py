from django.shortcuts import render
from rest_framework.views import APIView


# Create your views here.
# 1.生成支付宝登录url

class PaymentView(APIView):
    """生成支付宝登录url"""

    def get(self, request):
        # 获取到美多商城订单编号
        # 校验订单编号
        # 创建alipay支付对象
        # 调用它里面的方法 生成支付宝登录url后面的 查询参数部分
        # 拼接完整 支付宝登录url
        # 沙箱环境 : 	https://openapi.alipaydev.com/gateway.do? + 查询参数部分
        # 真实环境 : 	https://openapi.alipay.com/gateway.do? + 查询参数部分

        pass

# 2.支付生成后的验证和修改订单状态 保存订单及支付流水号