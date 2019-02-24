from django.conf.urls import url
from . import views
urlpatterns=[
    url(r'^sina/authorization/$',views.WeiboAuthURLView.as_view()),
    url(r'^sina/user/$', views.SinaWeiBoUserView.as_view()),
]