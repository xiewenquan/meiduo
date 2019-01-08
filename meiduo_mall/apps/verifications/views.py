import random
from django.http import HttpResponse
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView
from libs.captcha.captcha import captcha
from libs.yuntongxun.sms import CCP
# Create your views here.


from verifications.serializers import RegisterSmscodeSerializer

#图片验证码
class RegisterImageAPIView(APIView):
    def get(self,request,image_code_id):
        #1.接受image_code_id，生成图片和验证码
        text,image=captcha.generate_captcha()
        #2.验证码保存到redis中
        #2.1链接redis
        redis_coon=get_redis_connection('code')
        #2.2设置图片
        redis_coon.setex('img_'+image_code_id,60,text)
        #3返回图片响应
        #注意,图片是二进制,我们通过HttpResponse返回
        return HttpResponse(image,content_type='image/jpeg')

#短信验证码
class RegisterSmscodeAPIView(APIView):

    def get(self,request,mobile):
        # 1.接收参数
        params = request.query_params
        # 2.校验参数  还需要验证码 用户输入的图片验证码和redis的保存 是否一致
        serializer = RegisterSmscodeSerializer(data=params)
        serializer.is_valid(raise_exception=True)
        # 3.生成短信
        sms_code = '%06d'%random.randint(0,999999)
        # 4.将短信保存在redis中
        redis_conn = get_redis_connection('code')

        redis_conn.setex('sms_'+mobile,5*60,sms_code)
        # 5.使用云通讯发送短信
        # CCP().send_template_sms(mobile,[sms_code,5],1)

        from celery_tasks.sms.tasks import send_sms_code
        # delay 的参数和 任务的参数对应
        # 必须调用 delay 方法
        send_sms_code.delay(mobile,sms_code)

        # 6.返回相应
        return Response({'msg':'ok'})





