from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from users import views

urlpatterns=[
    #判断用户名
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.RegisterUsernameAPIView.as_view(), name='usernamecount'),
    # 判断手机号
    url(r'^phones/(?P<mobile>1[345789]\d{9})/count/$', views.RegisterPhoneCountAPIView.as_view(), name='phonecount'),
    #
    url(r'^$',views.RegiserUserAPIView.as_view()),
    #实现认证
    url(r'^auths/$', obtain_jwt_token),
    #用户中心
    url(r'infos/$',views.UserCenterInfoAPIView.as_view())
]