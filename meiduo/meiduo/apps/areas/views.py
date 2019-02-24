from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.mixins import CacheResponseMixin
# Create your views here.

from .models import Area
from .serializers import AreaSerializer,SubsAreaSerializer

"""
    为什么要用ReadOnlyModelViewSet
    对数据查询操作
    既可以查单一数据(retrieve行为),有可以查列表数据(list)
    数据也都来源一个张表
"""


class AeraViewSet(CacheResponseMixin,ReadOnlyModelViewSet):
    """行政区划信息"""
    pagination_class = None  # 区划信息不分页


    # queryset = Area.objects.filter(parent_id=None)
    def get_queryset(self):
        if self.action == 'list':
              queryset = Area.objects.filter(parent_id=None)# 如果是list行为表示要所有省的模型
              return queryset
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return AreaSerializer
        else:
            return SubsAreaSerializer




        # serializer_class = AreaSerializer

# class AeraViewSet(ReadOnlyModelViewSet):
#     """行政区划信息"""
#  如果修改的话只能查到所有的,不能按照省市区查询
#     pagination_class = None  # 区划信息不分页
#
#     queryset = Area.objects.all()
#     serializer_class = AreaSerializer




