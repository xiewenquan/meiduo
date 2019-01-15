from rest_framework import serializers

from goods.models import SKU


class HotSKUListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'comments')
