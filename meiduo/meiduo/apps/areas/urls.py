from rest_framework.routers import DefaultRouter
from django.conf.urls import url
from . import views
urlpatterns=[
    # url(r'^areas/$', views.AeraViewSet.as_view({'get': 'list'}))
]

router= DefaultRouter()
# 使用DefaultRouter 生成路由,不用/和$
router.register(r'areas',views.AeraViewSet, base_name='areas')
urlpatterns += router.urls