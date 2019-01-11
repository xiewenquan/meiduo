from QQLoginTool.QQtool import OAuthQQ
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from meiduo_mall import settings
from oauth.models import OAuthQQUser
from oauth.serializers import OAuthQQUserSerializer
from oauth.utils import generic_open_id

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

        return Response({"auth_url":login_url})      #code=AA6CCF6AA153104C94D90B51FDCB8954&state



"""
在QQ将用户重定向到此网页的时候，重定向的网址会携带QQ提供的code参数，用于获取用户信息使用，
我们需要将这个code参数发送给后端，在后端中使用code参数向QQ请求用户的身份信息，并查询与该QQ用户绑定的用户。
"""

"""
1. 用户同意授权登陆,这个时候 会返回一个 code
2. 我们用code 换取 token
3. 有了token,我们再获取 openid
"""
"""
1.分析需求 (到底要干什么)
    前端会接收到 用户同意之后的, code 前端应该将这个code 发送给后端
2.把需要做的事情写下来(把思路梳理清楚)
3.路由和请求方式   /oauth/qq/users/?code=xxxxxx    GET
4.确定视图
    1. 接收这个数据
    2. 用code换token
    3. 用token换openid
5.按照步骤实现功能
"""

class OAuthQQUserAPIView(APIView):
    # 获取用户openid
    def get(self,request):

        #1.接收数据
        params = request.query_params
        code=params.get('code')
        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        #2.code--->token
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)
        token=oauth.get_access_token(code)

        #3.token--->openid
        openid=oauth.get_open_id(token)

        # 根据openid查询数据
        try:
            qquser=OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            #库中不存在
            token = generic_open_id(openid)

            return Response({'access_token':token})


        else:
            # 存在,应该让用户登陆
            from rest_framework_jwt.settings import api_settings

            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(qquser.user)
            token = jwt_encode_handler(payload)

            return Response({
                'token':token,
                'username':qquser.user.username,
                'user_id':qquser.user.id
            })


    """
    当用户点击绑定的时候 ,我们需要将 手机号,密码,短信验证码和加密的openid 传递过来
    1. 接收数据
    2. 对数据进行校验
    3. 保存数据
    4. 返回相应
    POST    /oauth/qq/users/
    """
    #OpenID绑定美多商城用户
    def post(self,request):

        #1.接收数据
        data=request.data

        #2.对数据进行校验
        serializer=OAuthQQUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        #3.保存数据
        qquser=serializer.save()

        #4.返回相应,应该有token 数据

        from rest_framework_jwt.settings import api_settings

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(qquser.user)
        token = jwt_encode_handler(payload)

        return Response({
            'token': token,
            'username': qquser.user.username,
            'user_id': qquser.user.id
        })

