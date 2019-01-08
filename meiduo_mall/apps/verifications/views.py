from django.http import HttpResponse
from django_redis import get_redis_connection
from rest_framework.views import APIView
from libs.captcha.captcha import captcha
from django.shortcuts import render

# Create your views here.

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

