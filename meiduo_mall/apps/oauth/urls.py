from django.conf.urls import url
from oauth.views import OAuthQQURLAPIView, OAuthQQUserAPIView

urlpatterns=[
    #跳转ｑｑ登陆界面
    url(r"qq/statues/$",OAuthQQURLAPIView.as_view()),

    url(r'^qq/users/$', OAuthQQUserAPIView.as_view()),
]