from QQLoginTool.QQtool import OAuthQQ
from rest_framework.response import Response
from rest_framework.views import APIView

from meiduo_mall import settings

"""
当用户点击qq按钮的时候,会发送一个请求,
我们后端返回给它一个 url (URL是根据文档来拼接出来的)
GET     /oauth/qq/statues/
"""

# 返回QQ登录网址的视图
class OAuthQQURLAPIView(APIView):
    def get(self,request):

        # next表示从哪个页面进入到的登录页面，将来登录成功后，就自动回到那个页面
        state = request.query_params.get('state')
        if not state:
            state = '/'

        # 获取QQ登录页面网址
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=state)

        login_url = oauth.get_qq_url()

        return Response({"auth_url":login_url})


