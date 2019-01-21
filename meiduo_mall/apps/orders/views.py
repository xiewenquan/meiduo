from _decimal import Decimal

from django_redis import get_redis_connection
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from orders.serializers import OrderPlaceSerializer, OrderSKUSerialzier

"""
订单列表展示

必须是登陆用户才可以访问

# 1. 我们获取用户信息
# 2. 从redis中获取数据
#     hash
#     set
# 3. 需要获取的是 选中的数据
# 4. [sku_id,sku_id]
# 5. [SKU,SKU,SKU]
# 6. 返回相应

GET     /orders/placeorders/
"""

class PlaceOrderAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):

        # 1. 我们获取用户信息
        user = request.user

        # 2. 从redis中获取数据
        redis_conn = get_redis_connection('cart')
        #     hash
        # {b'sku_id':b'count'}
        redis_id_count = redis_conn.hgetall('cart_%s'%user.id)
        #     set
        # [b'sku_id']
        selected_ids = redis_conn.smembers('cart_selected_%s' % user.id)
        # 3. 需要获取的是 选中的数据,同时对bytes类型进行转换
        selected_cart = {}

        for sku_id in selected_ids:
            selected_cart[int(sku_id)] = int(redis_id_count[sku_id])

        # 4. [sku_id,sku_id]
        ids = selected_cart.keys()

        # 5. [SKU,SKU,SKU]
        skus = SKU.objects.filter(pk__in=ids)

        for sku in skus:
            sku.count = selected_cart[sku.id]

        # 6. 返回相应
        freight = Decimal('10.00')

        serializer = OrderPlaceSerializer({
            'freight':freight,
            'skus':skus
        })
        # serializer = OrderSKUSerialzier(skus, many=True)

        return Response(serializer.data)



