import base64
import pickle

from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from carts.serializers import CartSerializer, CartSKUSerializer, CartDeleteSerializer
from goods.models import SKU

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
    # def post(self,request):
    #     """
    #     添加购物车的业务逻辑是:
    #     用户点击 添加购物车按钮的时候,前端需要收集数据:
    #     商品id,个数,选中状态默认为True,用户信息
    #
    #     1.接收数据
    #     2.校验数据(商品是否存在,商品的个数是否充足)
    #     3.获取校验之后的数据
    #     4.获取用户信息
    #     5.根据用户的信息进行判断用户是否登陆
    #     6.登陆用户保存在redis中
    #         6.1 连接redis
    #         6.2 将数据保存在redis中的hash 和 set中
    #         6.3 返回相应
    #     7.未登录用户保存在cookie中
    #         7.1 先获取cookie数据
    #         7.2 判断是否存在cookie数据
    #         7.3 如果添加的购物车商品id存在 则进行商品数量的累加
    #         7.4 如果添加的购物车商品id不存在 则直接添加商品信息
    #         7.5 返回
    #     """
    #
    #     data=request.data
    #
    #     serializer=CartSerializer(data=data)
    #     serializer.is_valid(raise_exception=True)
    #
    #     sku_id=serializer.validated_data.get('sku_id')
    #     count=serializer.validated_data.get('count')
    #     selected=serializer.validated_data.get('selected')
    #
    #     try:
    #         user=request.user
    #     except Exception as e :
    #         user=None
    #
    #     if user is not None and user.is_authenticated:
    #         redis_conn=get_redis_connection('cart')
    #         redis_conn.hset('cart_%s'%user.id,sku_id,count)
    #         redis_conn.hincrby('cart_%s' % user.id, sku_id, count)
    #
    #         if selected:
    #             redis_conn.sadd('cart_selected_%s'%user.id,sku_id)
    #
    #             return Response(serializer.data)
    #
    #     else:
    #         cookie_str=request.COOKIES.get('cart')
    #         if cookie_str is not None:
    #             decode=base64.b64decode(cookie_str)
    #             cookie_cart=pickle.loads(decode)
    #         else:
    #             cookie_cart={}
    #
    #         if sku_id in cookie_cart:
    #             origin_count=cookie_cart[sku_id]['count']
    #             count += origin_count
    #
    #         cookie_cart[sku_id]={
    #             'count':count,
    #             'selected':selected
    #         }
    #
    #         dumps=pickle.dumps(cookie_cart)
    #         encode=base64.b64encode(dumps)
    #         value=encode.decode()
    #
    #         response= Response(serializer.data)
    #         response.set_cookie('cart',value)
    #
    #         return response

    #GET         cart/           获取购物车数据

    def post(self, request):
        # 1.接收数据
        data = request.data
        # 2.校验数据(商品是否存在,商品的个数是否充足)
        serializer = CartSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # 3.获取校验之后的数据
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')
        # 4.获取用户信息
        try:
            user = request.user
        except Exception as e:
            user = None
        # 5.根据用户的信息进行判断用户是否登陆
        # request.user.is_authenticated
        if user is not None and user.is_authenticated:
            # 6.登陆用户保存在redis中
            #     6.1 连接redis
            redis_conn = get_redis_connection('cart')
            #     6.2 将数据保存在redis中的hash 和 set中
            # hash  cart_userid: sku_id:count
            # 应该累加数据
            # redis_conn.hset('cart_%s'%user.id,sku_id,count)

            # redis_conn.hincrby('cart_%s'%user.id,sku_id,count)
            # # set  cart_selected_userid: sku_id
            # if selected:
            #     redis_conn.sadd('cart_selected_%s'%user.id,sku_id)



            # 管道① 创建管道
            pl = redis_conn.pipeline()

            # 管道② 将指令添加到管道中
            pl.hincrby('cart_%s' % user.id, sku_id, count)
            # set  cart_selected_userid: sku_id
            if selected:
                pl.sadd('cart_selected_%s' % user.id, sku_id)

            # 管道③  执行
            pl.execute()

            #     6.3 返回相应
            return Response(serializer.data)

        else:
            # cart: {}

            # 7.未登录用户保存在cookie中
            #     7.1 先获取cookie数据
            cookie_str = request.COOKIES.get('cart')
            #     7.2 判断是否存在cookie数据
            if cookie_str is not None:
                # 说明有数据
                # ① 对base64数据进行解码
                decode = base64.b64decode(cookie_str)
                # ② 将二进制转换位字典
                cookie_cart = pickle.loads(decode)
            else:
                # 说明没有数据
                # 初始化
                cookie_cart = {}

            # 7.3 如果添加的购物车商品id存在 则进行商品数量的累加
            # cookie_cart = {sku_id: {count:xxx,selected:xxx}}
            if sku_id in cookie_cart:
                # 存在
                # 原个数
                origin_count = cookie_cart[sku_id]['count']
                # 现个数  count = count+origin_count
                count += origin_count
            # 7.4 如果添加的购物车商品id不存在 则直接添加商品信息
            # cookie_cart = {sku_id: {count:xxx,selected:xxx}}
            cookie_cart[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 7.5 对字典进行处理
            # 7.5.1 将字典转换为二进制
            dumps = pickle.dumps(cookie_cart)
            # 7.5.2 进行base64的编码
            encode = base64.b64encode(dumps)
            # 7.5.3 将bytes类型转换为str
            value = encode.decode()

            #     7.6 返回相应
            response = Response(serializer.data)

            response.set_cookie('cart', value)

            return response



    def get(self,request):

        # 1.接收用户信息
        try:
            user=request.user
        except Exception as e:
            user=None

        # 2.根据用户信息进行判断
        if user is not None and user.is_authenticated:

            # 3.登陆用户从redis中获取数据
            #     3.1 连接redis
            redis_conn = get_redis_connection('cart')
            #     3.2 hash        cart_userid:            {sku_id:count}
            #         set         cart_selected_userid:   sku_id
            #         获取hash的所有数据
            redis_ids_count=redis_conn.hgetall('cart_%s'%user.id)
            #         [sku_id,sku_id]
            # 获取set数据
            redis_selected_ids=redis_conn.smembers('cart_selected_%s'%user.id)

            # redis获取的数据是 bytes类型的,我们将它转换为 cookie的数据格式
            cookie_cart={}
            for sku_id,count in redis_ids_count.items():
                cookie_cart[int(sku_id)]={
                    'count':int(count),
                    'selected':sku_id in redis_selected_ids
                }

        else:
            # 4.未登陆用户从cookie中获取数据
            #     4.1 先从cookie中获取数据
            cookie_str=request.COOKIES.get('cart')
            #     4.2 判断是否存在购物车数据
            if cookie_str is not None:
                #将base64数据进行解码
                decode=base64.b64decode(cookie_str)
                #将二进制转换为字典
                cookie_cart=pickle.loads(decode)
            else:
                cookie_cart={}
            #         {sku_id:{count:xxx,selected:xxxx}}
            #
            #         [sku_id,sku_id]

        # 5 根据商品id,获取商品的详细信息
        ids=cookie_cart.keys()
        skus=SKU.objects.filter(pk__in=ids)
        #对商品列表数据进行便利，来动态的添加count和选中状态
        for sku in skus:
            sku.count=cookie_cart[sku.id]['count']
            sku.seleted=cookie_cart[sku.id]['selected']
        # 6 返回相应
        serializer = CartSKUSerializer(skus,many=True)

        return Response(serializer.data)


    #PUT         cart/           修改购物车
    def put(self,request):
        #前端需要将商品id,count(个数 是采用的将最终数量提交给后端),selected提交给后端

        # 1.接收数据
        data=request.data

        # 2.校验数据
        serializer=CartSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # 3.获取验证之后的数据
        sku_id=serializer.validated_data.get('sku_id')
        count=serializer.validated_data.get('count')
        selected=serializer.validated_data.get('selevted')

        # 4.获取用户信息
        try:
            user=request.user
        except Exception as e:
            user=None

        # 5.根据用户的登陆状态进行判断
        if user is not None and user.is_authenticated:

            # 6.登陆用户redis
            #     6.1 连接redis
            redis_conn=get_redis_connection('cart')
            #     6.2 更新数据
            #hash
            redis_conn.hset('cart_%s'%user.id, sku_id, count)
            #set
            if selected:
                # 选中,则添加到set中
                redis_conn.sadd('cart_selected_%s'%user.id, sku_id)
            else:
                # 取消选中,应该删除
                redis_conn.srem('cart_selected_%s'%user.id, sku_id)

            #     6.3 返回相应
            # 必须要将数据返回回去
            # 因为前端是将 个数的终值 传递过来的,我们要返回回去
            return Response(serializer.data)

        else:
        # 7.未登录用户cookie
        #     7.1 获取cookie数据
            cookie_str=request.COOKIES.get('cart')
        #     7.2 判断cart数据是否存在
            if cookie_str is not None:
                cookie_cart=pickle.loads(base64.b64decode(cookie_str))
            else:
                cookie_cart={}
        #     7.3 更新数据
            if sku_id in cookie_cart:
                cookie_cart[sku_id]={
                    'count':count,
                    'selected':selected
                }
        #     7.4 返回相应
            response=Response(serializer.data)
            value=base64.b64encode(pickle.dumps(cookie_cart)).decode()
            response.set_cookie('cart',value)
            return response


    #DELETE      cart/           删除购物车
    def delete(self,request):

        # 1.后端接收数据
        data=request.data
        # 2.校验数据
        serializer=CartDeleteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # 3.获取校验之后的数据
        sku_id=serializer.validated_data.get('sku_id')
        # 4.获取用户信息
        try:
            user=request.user
        except Exception as e:
            user=None
        # 5.根据用户信息进行判断
        if user is not None and user.is_authenticated:

            # 6.登陆用户redis
            #     6.1 连接redis
            redis_conn =get_redis_connection('cart')
            #     6.2 删除数据
            #hash
            redis_conn.hdel('cart_%s'%user.id, sku_id)
            #set
            redis_conn.srem('cart_selected_%s'%user.id, sku_id)
            #     6.3 返回相应
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # 7.未登录用户cookie
            #     7.1 获取cookie数据
            cookie_str=request.COOKIES.get('cart')
            #     7.2 判断cart数据是否存在
            if cookie_str is not None:
                cookie_str=pickle.loads(base64.b64decode(cookie_str))
            else:
                cookie_str={}
            #     7.3 删除指定数据
            if sku_id in cookie_str:
                del cookie_str[sku_id]
            #     7.4 返回相应
            response=Response(status=status.HTTP_204_NO_CONTENT)
            value=base64.b64encode(pickle.dumps(cookie_str)).decode()
            response.set_cookie('cart', value)

            return response
