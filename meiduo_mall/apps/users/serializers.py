import re
from rest_framework import serializers
from users.models import User
from django_redis import get_redis_connection


class  RegiserUserSerializer(serializers.ModelSerializer):

    sms_code=serializers.CharField(label='短信验证码',max_length=6,min_length=6,write_only=True,required=True,allow_blank=False)
    allow=serializers.CharField(label='是否同意协议',required=True,allow_null=False,write_only=True)
    password2=serializers.CharField(label='确认密码',required=True,allow_null=False,write_only=True)

    token = serializers.CharField(label='token', read_only=True)
    """
    ModelSerializer 自动生成字段的过程会对 fields 进行遍历, 先去 model中查看是否有相应的字段
    如果有 则自动生成
    如果没有 则查看当前类 是否有定义
    """
    class Meta:
        model = User
        fields = ['mobile','token','username','password','sms_code','allow','password2']
    """
    校验数据
    1. 字段类型
    2. 字段选项
    3. 单个字段
    4. 多个字段
    mobile: 符合手机号规则
    allow: 是否同意协议
    两次密码需要一致
    短信
    """
    #单个字段
    def validate_mobile(self,value):
        if not re.match(r'1[3-9]\d{9}',value):
            raise serializers.ValidationError('手机号不符合规则')
        return value

    def validate_allow(self,value):
        if value != 'true':
            raise serializers.ValidationError('没有同意协议')
        return value

    #多个字段
    def validate(self, attrs):
        #1两次密码需要一致
        password = attrs['password']
        password2 = attrs['password2']
        if password!=password2:
            raise serializers.ValidationError('密码不一致')
        #2短信
        # 2.1 获取用户提交的
        mobile = attrs.get('mobile')
        sms_code = attrs['sms_code']
        # 2.2 获取 redis
        redis_conn = get_redis_connection('code')
        redis_code = redis_conn.get('sms_'+mobile)
        if redis_code is None:
            raise serializers.ValidationError('短信验证码已过期')
        # 最好删除短信
        redis_conn.delete('sms_'+mobile)
        #2.3 比对
        if redis_code.decode() != sms_code:
            raise serializers.ValidationError('验证码不一致')

        return attrs

    def create(self, validated_data):
        del validated_data['sms_code']
        del validated_data['allow']
        del validated_data['password2']

        # 现在的数据满足要求了, 可以让父类去执行
        user = super().create(validated_data)

        #密码加密
        user.set_password(validated_data['password'])
        user.save()

        # 用户入库之后,我们生成token
        from rest_framework_jwt.settings import api_settings

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        user.token=token

        return user

