from django.shortcuts import render
from django.views import View
from django import http
from meiduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection

from meiduo_mall.libs.yuntongxun.sms import CCP
import random

from meiduo_mall.utils.response_code import RET
from verifications import constants


class ImageCodeView(View):
    def get(self,request,image_code_id):

        #1,生成图片验证码
        text,image_data =  captcha.generate_captcha()

        #2,保存图片验证码到redis中
        redis_conn = get_redis_connection("code")
        #分别对应的参数,key, time , value
        redis_conn.setex("image_code_%s"%image_code_id,constants.REDIS_IMAGE_CODE_EXPIRES,text)

        #3,返回响应
        return http.HttpResponse(image_data,content_type="image/png")

class SmsCodeView(View):
    def get(self,request,mobile):
        #1,获取参数
        image_code = request.GET.get("image_code")
        image_code_id = request.GET.get("image_code_id")

        #2,校验参数
        #2,1 为空校验
        if not all([image_code,image_code_id]):
            return http.JsonResponse({"errmsg":"参数不全","code":RET.PARAMERR})

        #2,2 校验图片验证码的正确性
        redis_conn = get_redis_connection("code")
        redis_image_code =  redis_conn.get("image_code_%s"%image_code_id)

        #判断是否过期
        if not redis_image_code:
            return http.JsonResponse({"errmsg": "图片验证码过期了", "code": RET.NODATA})

        #删除
        redis_conn.delete("image_code_%s"%image_code_id)

        #正确性
        if image_code.lower() != redis_image_code.decode().lower():
            return http.JsonResponse({"errmsg": "图片验证码错误", "code":RET.DATAERR})

        #3,发送短信
        sms_code = "%06d"%random.randint(0,999999)
        print("sms_code = %s"%sms_code)
        # ccp = CCP()
        # ccp.send_template_sms(mobile, [sms_code, constants.REDIS_SMS_CODE_EXPIRES/60], 1)

        #保存到redis中
        redis_conn.setex("sms_code_%s"%mobile,constants.REDIS_SMS_CODE_EXPIRES,sms_code)

        #4,返回响应
        return http.JsonResponse({"errmsg":"发送成功","code":RET.OK})