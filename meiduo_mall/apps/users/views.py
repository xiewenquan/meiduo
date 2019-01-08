from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

#判断用户名是否存在
# 1.分析需求
# 2.请求方式	GET
# 3.URL路由定义： /users/usernames/(?P<username>\w{5,20})/count/
# 4.确定视图（接口）
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User

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

