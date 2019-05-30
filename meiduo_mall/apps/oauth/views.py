from django.contrib.auth import login
from django.shortcuts import render, redirect
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django import http
from django.views import View
import re
from django_redis import get_redis_connection
from oauth.utils import generate_sign_openid,decode_sign_openid
from users.models import User
from .models import OAuthQQUser


class OAuthQQLoginView(View):
    def get(self,request):
        #1,获取参数
        state = request.GET.get("next","/")

        #2,创建OAuthQQ对象
        oauth_qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                client_secret=settings.QQ_CLIENT_SECRET,
                redirect_uri=settings.QQ_REDIRECT_URI,
                state=state)

        #3,获取qq登陆页面
        login_url = oauth_qq.get_qq_url()

        #4,返回
        return http.JsonResponse({"login_url":login_url})

class OAuthUserView(View):
    def get(self,request):
        #1,获取参数,code
        code = request.GET.get("code")
        state = request.GET.get("state","/")

        if not code:
            return http.HttpResponseForbidden("code丢了")

        #2,通过code换取access_token
        oauth_qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                           client_secret=settings.QQ_CLIENT_SECRET,
                           redirect_uri=settings.QQ_REDIRECT_URI,
                           state=state)
        access_token = oauth_qq.get_access_token(code)

        #3,通过access_token换取openid
        openid = oauth_qq.get_open_id(access_token)

        #4,根据openid,取到qq用户的对象
        try:
            oauth_qq_user = OAuthQQUser.objects.get(openid=openid)

        except OAuthQQUser.DoesNotExist:
            #初次授权
            sign_openid = generate_sign_openid(openid)
            return render(request,'oauth_callback.html',context={"token":sign_openid})
        else:
            #5,非初次授权
            user = oauth_qq_user.user

            #5,1状态保持
            login(request,user)
            request.session.set_expiry(3600*24*2)

            #5,2,返回响应
            response = redirect("/")
            response.set_cookie("username",user.username)
            return response

    def post(self,request):
        #1,获取参数
        sign_openid = request.POST.get("access_token")
        mobile = request.POST.get("mobile")
        pwd = request.POST.get("pwd")
        sms_code = request.POST.get("sms_code")

        #2,校验参数
        #2,1为空校验
        if not all([sign_openid,mobile,pwd,sms_code]):
            return http.HttpResponseForbidden("参数不全")

        #2,2 校验sign_openid是否证券
        openid = decode_sign_openid(sign_openid)
        if not openid:
            return http.HttpResponseForbidden("openid过期")

        #2,3 校验手机号的格式
        if not re.match(r'^1[3-9]\d{9}$',mobile):
            return http.HttpResponseForbidden("手机号格式有误")

        #2,4 校验密码的格式
        if not re.match(r'^[0-9a-zA-Z]{8,20}$', pwd):
            return http.HttpResponseForbidden("密码格式有误")

        #2,5 校验短信验证码的正确性
        redis_conn = get_redis_connection("code")
        redis_sms_code = redis_conn.get("sms_code_%s"%mobile)

        if not redis_sms_code:
            return http.HttpResponseForbidden("短信验证码已过期")

        if sms_code != redis_sms_code.decode():
            return http.HttpResponseForbidden("短信验证码填写错误")

        #3,判断是否存在美多用户,如果存在直接绑定,如果不存在直接创建用户再绑定
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            #3,1创建美多用户
            user = User.objects.create_user(username=mobile,password=pwd,mobile=mobile)

            #3,2绑定美多用户和qq用户
            OAuthQQUser.objects.create(openid=openid,user=user)

            # 3.3,状态保持
            login(request, user)
            request.session.set_expiry(3600 * 24 * 2)

            # 3.4,返回到首页中
            response = redirect("/")
            response.set_cookie("username", user.username, max_age=3600 * 24 * 2)
            return response
        else:
            #4.1校验密码正确性
            if not user.check_password(pwd):
                return http.HttpResponseForbidden("密码错误")

            #4,2绑定美多用户和qq用户
            OAuthQQUser.objects.create(openid=openid,user=user)

            #4.3,状态保持
            login(request,user)
            request.session.set_expiry(3600*24*2)

            #4.4,返回到首页中
            response = redirect("/")
            response.set_cookie("username",user.username,max_age=3600*24*2)
            return response
