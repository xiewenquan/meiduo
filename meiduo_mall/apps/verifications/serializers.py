from django_redis import get_redis_connection
from rest_framework import serializers


class RegisterSmscodeSerializer(serializers.Serializer):
    #用户输入的验证码
    text=serializers.CharField(max_length=4,min_length=4,required=True)
    image_code_id=serializers.UUIDField(required=True)

    def validate(self, attrs):
        #1.获取用户提交的验证码
        text=attrs.get('text')
        #2.获取redis 的验证码
        redis_conn=get_redis_connection('code')
        image_id=attrs.get('image_code_id')
        redis_text=redis_conn.get('img'+str(image_id))
        if redis_text is None:
            raise serializers.ValidationError("图片验证码过期")

        #3.比对
        if redis_text.decode().lower() != text.lower():
            raise serializers.ValidationError("输入错误")
        return attrs


