import base64
import pickle

from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from carts.serializers import CartSerializer

"""
1. 未登录用户的数据是保存在 cookie中
    登录用户的数据是保存在 Redis

2. cookie数据 我们需要保存 商品id,个数,选中状态
  Redis数据 我们需要保存 商品id,个数,选中状态

3. 组织cookie的数据结构
   cart =  {
        sku_id:{ count:3,selected:True},
        sku_id:{ count:3,selected:True},
    }

    redis是保存在内存中 Redis的数据的设计原则: 占用最少的空间 满足我们的需求

    登陆用户的数据
    组织Redis的数据结构
    #商品id,个数,选中状态
    Hash(所有id,count)       hash_key:   property:value

                            cart_userid: sku_id:count

    Set(记录选中的id)         cart_selected_userid:  sku_id
4. 判断用户是否登陆
    request.user
    如果用户的token过期了/伪造的 我们需要重写 perform_authentication 方法
    让视图 先不要进行身份认证
    当我们需要的时候再来认证
5. base64
"""

"""
POST        cart/           新增购物车
GET         cart/           获取购物车数据
PUT         cart/           修改购物车
DELETE      cart/           删除购物车
"""
from django_redis import get_redis_connection
class CartAPIView(APIView):

    #重写认证方法，将token 被篡改的用户也能够添加购物车，最后再进行用户确认
    def perform_authentication(self, request):
        pass

    #POST        cart/           新增购物车
    def post(self,request):
        """
        添加购物车的业务逻辑是:
        用户点击 添加购物车按钮的时候,前端需要收集数据:
        商品id,个数,选中状态默认为True,用户信息

        1.接收数据
        2.校验数据(商品是否存在,商品的个数是否充足)
        3.获取校验之后的数据
        4.获取用户信息
        5.根据用户的信息进行判断用户是否登陆
        6.登陆用户保存在redis中
            6.1 连接redis
            6.2 将数据保存在redis中的hash 和 set中
            6.3 返回相应
        7.未登录用户保存在cookie中
            7.1 先获取cookie数据
            7.2 判断是否存在cookie数据
            7.3 如果添加的购物车商品id存在 则进行商品数量的累加
            7.4 如果添加的购物车商品id不存在 则直接添加商品信息
            7.5 返回
        """

        data=request.data

        serializer=CartSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        sku_id=serializer.validated_data.get('sku_id')
        count=serializer.validated_data.get('count')
        selected=serializer.validated_data.get('selected')

        try:
            user=request.user
        except Exception as e :
            user=None

        if user is not None and user.is_authenticated:
            redis_conn=get_redis_connection('cart')
            redis_conn.hset('cart_%s'%user.id,sku_id,count)
            if selected:
                redis_conn.sadd('cart_selected_%s'%user.id,sku_id)

                return Response(serializer.data)

        else:
            cookie_str=request.COOKIES.get('cart')
            if cookie_str is not None:
                decode=base64.b64decode(cookie_str)
                cookie_cart=pickle.loads(decode)
            else:
                cookie_cart={}

            if sku_id in cookie_cart:
                origin_count=cookie_cart[sku_id]['count']
                count += origin_count
            cookie_cart[sku_id]={
                'count':count,
                'selected':selected
            }

            dumps=pickle.dumps(cookie_cart)
            encode=base64.b64encode(dumps)
            value=encode.decode()

            response= Response(serializer.data)
            response.set_cookie('cart',value)

            return response