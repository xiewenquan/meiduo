from django.conf.urls import url
from oauth.views import OAuthQQURLAPIView

urlpatterns=[
    #跳转ｑｑ登陆界面
    url(r"qq/statues/$",OAuthQQURLAPIView.as_view())
]