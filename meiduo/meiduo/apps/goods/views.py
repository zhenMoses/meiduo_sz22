from django.shortcuts import render
from rest_framework.generics import ListAPIView

from .models import SKU
from .serializers import SKUSerializer


# Create your views here.
# /categories/(?P<category_id>\d+)/skus?page=xxx&page_size=xxx&ordering=xxx

class SKUListView(ListAPIView):
    """商品列表界面"""

    # 指定序列化器
    serializer_class = SKUSerializer

    # 指定查询集
    # queryset = SKU.objects.filter(is_launched=True, category_id=category_id)

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')  # 获取url路径中的正则组别名提取出来的参数
        return SKU.objects.filter(is_launched=True, category_id=category_id)
