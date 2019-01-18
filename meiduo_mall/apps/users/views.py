from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

#判断用户名是否存在
# 1.分析需求
# 2.请求方式	GET
# 3.URL路由定义： /users/usernames/(?P<username>\w{5,20})/count/
# 4.确定视图（接口）
from django_redis import get_redis_connection
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from goods.models import SKU
from users.models import User
from users.serializers import RegiserUserSerializer, UserCenterInfoSerializer, UserEmailInfoSerializer, \
    AddressSerializer, AddUserBrowsingHistorySerializer, SKUSerializer

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


# class AddressViewSet(mixins.ListModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,GenericViewSet):
#     """
#     用户地址新增与修改
#     list GET: /users/addresses/
#     create POST: /users/addresses/
#     destroy DELETE: /users/addresses/
#     action PUT: /users/addresses/pk/status/
#     action PUT: /users/addresses/pk/title/
#     """
#
#     #制定序列化器
#     serializer_class = AddressSerializer
#     #添加用户权限
#     permission_classes = [IsAuthenticated]
#     #由于用户的地址有存在删除的状态,所以我们需要对数据进行筛选
#     def get_queryset(self):
#         return self.request.user.addresses.filter(is_deleted=False)
#
#     def create(self, request, *args, **kwargs):
#         """
#         保存用户地址数据
#         """
#         count = request.user.addresses.count()
#         if count >= 20:
#             return Response({'message':'保存地址数量已经达到上限'},status=status.HTTP_400_BAD_REQUEST)
#
#         # return super().create(request,*args,**kwargs)


"""
1.分析需求 (到底要干什么)
2.把需要做的事情写下来(把思路梳理清楚)
3.路由和请求方式
4.确定视图
5.按照步骤实现功能

新增地址
1. 后端接收数据
2. 对数据进行校验
3. 数据入库
4. 返回相应
POST        /users/addresses/
"""
#APIView                        基类
#GenericAPIVIew                 对列表视图和详情视图做了通用支持,一般和mixin配合使用
#CreateAPIView                   封装好了
from rest_framework.generics import CreateAPIView
from rest_framework.generics import GenericAPIView

class UserAddressAPIView(CreateAPIView):

    serializer_class = AddressSerializer

    # queryset =  新增数据用不到该属性



"""
最近浏览记录
1. 必须是登陆用户的 我们才记录浏览记录
2. 在详情页面中添加 , 添加商品id 和用户id
3. 把数据保存在数据库中是没问题的
4. 我们把数据保存在redis的列表中 (回顾redis)
"""

"""
添加浏览记录的业务逻辑
1. 接收商品id
2. 校验数据
3. 数据保存到redis中
4. 返回相应
post    /users/histories/
"""

#APIView                        基类
#GenericAPIVIew                 对列表视图和详情视图做了通用支持,一般和mixin配合使用
#CreateAPIView                   封装好了
from rest_framework.generics import CreateAPIView
from rest_framework.mixins import ListModelMixin
class UserHistoryAPIView(CreateAPIView):



    permission_classes = [IsAuthenticated]

    serializer_class = AddUserBrowsingHistorySerializer


    """
    获取浏览记录数据
    1. 从redis中获取数据   [1,2,3]
    2. 根据id查询数据     [SKU,SKU,SKU]
    3. 使用序列化器转换数据
    4. 返回相应
    """

    def get(self,request):

        user= request.user
        #1 从redis 获取数据
            #1.1链接redis
        redis_conn = get_redis_connection('history')
        ids = redis_conn.lrange('history_%s' % user.id, 0, 4)
        #2. 根据id查询数据
        skus=[]
        for id in ids:
            sku=SKU.objects.get(pk=id)
            skus.append(sku)
        #3.使用序列化器转换数据
        serializer=SKUSerializer(skus,many=True)
        #4.返回响应
        return Response(serializer.data)