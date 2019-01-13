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
from users.serializers import RegiserUserSerializer, UserCenterInfoSerializer, UserEmailInfoSerializer


#判断用户是否注册
from users.utils import check_token


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
#用户中心 方式一
# class UserCenterInfoAPIView(APIView):
#
#     permission_classes = [IsAuthenticated]
#
#     def get(self,request):
#         #接收数据
#         user = request.user
#         #将模型转换为字典（JSON）
#         serializer = UserCenterInfoSerializer(user)
#         #返回响应
#         return Response(serializer.data)


#用户中心 方式二
from rest_framework.generics import RetrieveAPIView
class UserCenterInfoAPIView(RetrieveAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = UserCenterInfoSerializer

    # queryset = User.objects.all()

    # 已有的父类不能满足我们的需求
    def get_object(self):

        return self.request.user


"""
1.分析需求 (到底要干什么)
2.把需要做的事情写下来(把思路梳理清楚)
3.路由和请求方式
4.确定视图
5.按照步骤实现功能

当用户 输入邮箱之后,点击保存的时候,
1.我们需要将 邮箱内容发送给后端,后端需要更新 指定用户的 email字段
2.同时后端需要给这个邮箱发送一个           激活连接
3.当用户点击激活连接的时候 ,改变 email_active的状态


用户 输入邮箱之后,点击保存的时候,
我们需要将 邮箱内容发送给后端

# 1. 后端需要接收 邮箱
# 2. 校验
# 3. 更新数据
# 4. 返回相应

PUT     /users/emails/
"""
#更新邮箱　方式一
# class UserEmailInfoAPIView(APIView):
#
#     permission_classes = [IsAuthenticated]
#
#     def put(self,request):
#         # 1. 后端需要接收 邮箱
#         data = request.data
#         # 2. 校验
#         serializer = UserEmailInfoSerializer(instance=request.user,data=data)
#         serializer.is_valid(raise_exception=True)
#         # 3. 更新数据
#         serializer.save()
#          # 发送邮件
#         # 4. 返回相应
#         return Response(serializer.data)


#更新邮箱　方式二
from rest_framework.generics import UpdateAPIView
#更新邮箱
class UserEmailInfoAPIView(UpdateAPIView):
    # 权限,必须是登陆用户才可以访问此接口
    permission_classes = [IsAuthenticated]

    serializer_class = UserEmailInfoSerializer

    # 父类方法 不能满足我们的需求
    def get_object(self):

        return self.request.user



"""
激活需求:
当用户点击激活连接的时候,需要让前端接收到 token信息
然后让前端发送 一个请求,这个请求 包含  token信息

1. 接收token信息
2. 对token进行解析
3. 解析获取user_id之后,进行查询
4. 修改状态
5. 返回相应

GET     /users/emails/verification/
"""

#APIView                        基类
#GenericAPIVIew                 对列表视图和详情视图做了通用支持,一般和mixin配合使用
#UpdateAPIView                   封装好了
from rest_framework import status
class UserEmailVerificationAPIView(APIView):

    def get(self,request):
        # 1. 接收token信息
        token = request.query_params.get('token')
        if token is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 2. 对token进行解析
        user_id = check_token(token)

        if user_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 3. 解析获取user_id之后,进行查询
        user = User.objects.get(pk=user_id)
        # 4. 修改状态
        user.email_active=True
        user.save()
        # 5. 返回相应
        return Response({'msg':'ok'})