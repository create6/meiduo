from django.shortcuts import render,redirect
from django.views import View
from django import http
import re
from .models import User

class RegisterView(View):
    def get(self,request):
        return render(request,'register.html')

    def post(self,request):
        #1,获取参数
        user_name = request.POST.get("user_name")
        pwd = request.POST.get("pwd")
        cpwd = request.POST.get("cpwd")
        phone = request.POST.get("phone")
        msg_code = request.POST.get("msg_code")
        allow = request.POST.get("allow")

        #2,校验参数
        #2,1 为空校验
        if not all([user_name,pwd,cpwd,phone,msg_code,allow]):
            return http.HttpResponseForbidden("参数不全")

        #2,2 两次密码校验
        if pwd != cpwd:
            return http.HttpResponseForbidden("两次密码不一致")

        #2,3 手机号格式校验
        if not re.match(r'1[3-9]\d{9}',phone):
            return http.HttpResponseForbidden("手机号格式有误")

        #2,4 短信验证码校验

        #2,5 协议校验
        if allow != 'on':
            return http.HttpResponseForbidden("必须同意协议")

        #3,创建用户对象,保存到数据库中
        user = User.objects.create_user(username=user_name,password=pwd,mobile=phone)

        #4,返回响应
        response = redirect("http://www.taobao.com")
        return response

class CheckUsernameView(View):
    def get(self,request,username):
        #1,根据用户名,查询用户数量
        count = User.objects.filter(username=username).count()

        #2,返回响应
        data = {
            "count":count
        }
        return http.JsonResponse(data)

class CheckMobileView(View):
    def get(self,request,mobile):
        #1,根据手机号,查询用户数量
        count = User.objects.filter(mobile=mobile).count()

        #2,返回响应
        data = {
            "count":count
        }
        return http.JsonResponse(data)