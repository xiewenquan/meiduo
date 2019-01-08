from django.conf.urls import url
from users import views

urlpatterns=[
    #判断用户名
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.RegisterUsernameAPIView.as_view(), name='usernamecount'),
    # 判断手机号
    url(r'^phones/(?P<mobile>1[345789]\d{9})/count/$', views.RegisterPhoneCountAPIView.as_view(), name='phonecount'),
]