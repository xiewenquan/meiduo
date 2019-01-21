from django_redis import get_redis_connection
from rest_framework import serializers

from goods.models import SKU
from orders.models import OrderInfo, OrderGoods


class OrderSKUSerialzier(serializers.ModelSerializer):
    count = serializers.IntegerField(label='个数', read_only=True)

    class Meta:
        model = SKU
        fields = ('id', 'count', 'name', 'default_image_url', 'price')


class OrderPlaceSerializer(serializers.Serializer):

    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)

    skus = OrderSKUSerialzier(many=True)