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
    url(r'infos/$',views.UserCenterInfoAPIView.as_view()),

    # users/emails/
    url(r'^emails/$',views.UserEmailInfoAPIView.as_view()),

    url(r'^emails/verification/$', views.UserEmailVerificationAPIView.as_view()),

]


# #设置视图集router
# from .views import AddressViewSet
# from rest_framework.routers import DefaultRouter
#
# router = DefaultRouter()
#
# router.register(r'addresses',AddressViewSet,base_name='address')
#
# urlpatterns += router.urls