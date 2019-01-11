from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

#判断用户名是否存在
# 1.分析需求
# 2.请求方式	GET
# 3.URL路由定义： /users/usernames/(?P<username>\w{5,20})/count/
# 4.确定视图（接口）
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
from users.serializers import RegiserUserSerializer, UserCenterInfoSerializer


#判断用户是否注册
class RegisterUsernameAPIView(APIView):

    def get(self,requset,username):
        #判断用户是否注册
        #查询用户名的数量
        #count=0  没有注册
        #count=1  已注册
        count = User.objects.filter(username=username).count()

        # 返回数据
        return Response({
            'count':count,
            'username':username
        })

#判断手机号是否存在
class RegisterPhoneCountAPIView(APIView):
    """
    查询手机号的个数
    GET: /users/phones/(?P<mobile>1[345789]\d{9})/count/
    """
    def get(self,request,mobile):

        #通过模型查询获取手机号个数
        count = User.objects.filter(mobile=mobile).count()
        #组织数据
        context = {
            'count':count,
            'phone':mobile
        }

        return Response(context)

#注册
class RegiserUserAPIView(APIView):

    def post(self,reqeust):
        # 1. 接收数据
        data = reqeust.data
        # 2. 校验数据
        serializer = RegiserUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # 3. 数据入库
        serializer.save()
        # 4. 返回相应
        return Response(serializer.data)


    """
    个人中心的 信息展示
    必须是登陆用户才可以访问

    1. 让前端传递 用户信息
    2. 我们根据用户的信息 来获取  user
    3. 将对象转换为字典数据

    GET     /users/infos/
    """
#拥护衷心
class UserCenterInfoAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):
        #接收数据
        user = request.user
        #将模型转换为字典（JSON）
        serializer = UserCenterInfoSerializer(user)
        #返回响应
        return Response(serializer.data)
