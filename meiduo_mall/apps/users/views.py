import json
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render,redirect
from django.views import View
from django import http
import re

from meiduo_mall.utils.email import generate_verify_url, decode_token
from meiduo_mall.utils.my_login_required import MyLoginRequiredMiXinView
from meiduo_mall.utils.response_code import RET
from .models import User
from django.contrib.auth import authenticate, login,logout
from django_redis import get_redis_connection
from celery_tasks.email.tasks import send_verify_url
from .models import Address
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
        redis_conn = get_redis_connection("code")
        redis_sms_code = redis_conn.get("sms_code_%s"%phone)
        if not redis_sms_code:
            return http.HttpResponseForbidden("短信验证码已过期")
        if msg_code != redis_sms_code.decode():
            return http.HttpResponseForbidden("短信验证码错误")

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

class LoginUserView(View):
    def get(self,request):
        return render(request,'login.html')

    def post(self,request):
        #1,获取参数
        username = request.POST.get("username")
        password = request.POST.get("pwd")
        remembered = request.POST.get("remembered")

        #2,校验参数
        #2,0 为空校验
        if not all([username,password]):
            return http.HttpResponseForbidden("参数不全")

        #2,1 用户名格式校验
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$',username):
            return http.HttpResponseForbidden("用户名格式有误")

        #2,2 密码格式校验
        if not re.match(r'^[0-9A-Za-z]{8,20}$',password):
            return http.HttpResponseForbidden("密码格式有误")

        #2,3 校验用户名和密码的正确性
        user = authenticate(request, username=username, password=password)

        if not user:
            return http.HttpResponseForbidden("账号或者密码错误")

        #3,状态保持
        login(request, user)

        #3,1设置状态保持的时间
        if remembered == "on":
            request.session.set_expiry(3600*24*2) #两天有效
        else:
            request.session.set_expiry(0)

        #4,返回响应
        response = redirect('/')
        response.set_cookie("username",user.username,3600*24*2)
        return response

class LogoutUserView(View):
    def get(self,request):
        #1,清除session
        logout(request)

        #2,清除cookie
        response = redirect('/')
        response.delete_cookie("username")
        return response

class UserCenterView(MyLoginRequiredMiXinView):

    def get(self,request):
        #1,组织数据
        context = {
            "username":request.user.username,
            "mobile":request.user.mobile,
            "email":request.user.email,
            "email_active":request.user.email_active
        }

        #2,返回页面渲染
        return render(request, 'user_center_info.html',context=context)

class EmailSendView(MyLoginRequiredMiXinView):
    def put(self,request):
        #1,获取参数
        dict_data = json.loads(request.body.decode())
        email = dict_data.get("email")

        #2,校验参数
        #2.1 为空校验
        if not email:
            return http.HttpResponseForbidden("参数不全")

        #2.2 格式校验
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
            return http.HttpResponseForbidden("邮件格式有误")

        #3,发送邮件
        verify_url = generate_verify_url(request.user)
        # send_mail(subject='美多商城邮箱激活',
        #           message=verify_url,
        #           from_email=settings.EMAIL_FROM,
        #           recipient_list=[email])
        send_verify_url.delay(verify_url,email) #celery发送邮件


        #4,数据入库
        request.user.email = email
        request.user.save()

        #5,返回响应
        return http.JsonResponse({"code":RET.OK,"errmsg":"ok"})

class EmailActiveView(View):
    def get(self,request):
        #1,获取token参数
        token = request.GET.get("token")

        #2,校验参数
        if not token:
            return http.HttpResponseForbidden("token丢失")

        user = decode_token(token)

        if not user:
            return http.HttpResponseForbidden("token过期")

        #3,数据入库(修改邮箱的激活器状态)
        user.email_active = True
        user.save()

        #4,返回响应(重定向到个人中心)
        return redirect('/info')

class AddressView(MyLoginRequiredMiXinView):
    def get(self,request):

        #1,获取用户所有的地址
        addresses =  request.user.addresses.filter(is_deleted=False)

        #2,数据拼接
        addresses_list = []
        for address in addresses:
            address_dict = {
                "id":address.id,
                "title":address.title,
                "receiver":address.receiver,
                "province":address.province.name,
                "city":address.city.name,
                "district":address.district.name,
                "place":address.place,
                "mobile":address.mobile,
                "tel":address.tel,
                "email":address.email,
                "province_id":address.province_id,
                "city_id":address.city_id,
                "district_id":address.district_id
            }
            addresses_list.append(address_dict)

        context = {
            "addresses":addresses_list,
            "default_address_id":request.user.default_address_id
        }

        #3,返回渲染页面
        return render(request,'user_center_site.html',context=context)

class AddressCreateView(MyLoginRequiredMiXinView):
    def post(self,request):
        #1,获取参数
        dict_data =  json.loads(request.body.decode())
        title = dict_data.get("title")
        receiver = dict_data.get("receiver")
        province_id = dict_data.get("province_id")
        city_id = dict_data.get("city_id")
        district_id = dict_data.get("district_id")
        place = dict_data.get("place")
        mobile = dict_data.get("mobile")
        tel = dict_data.get("tel")
        email = dict_data.get("email")

        #2,校验参数
        if not all([title,receiver,province_id,city_id,district_id,place,mobile,tel,email]):
            return http.HttpResponseForbidden("参数不全")

        #3,数据入库
        dict_data["user"] = request.user
        address = Address.objects.create(**dict_data)

        #4,返回响应
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email,
            "province_id": address.province_id,
            "city_id": address.city_id,
            "district_id": address.district_id
        }
        return http.JsonResponse({"code":RET.OK,"address":address_dict})

class AddressUpdateView(MyLoginRequiredMiXinView):
    def put(self,request,address_id):
        #1,获取参数
        dict_data =  json.loads(request.body.decode())
        title = dict_data.get("title")
        receiver = dict_data.get("receiver")
        province_id = dict_data.get("province_id")
        city_id = dict_data.get("city_id")
        district_id = dict_data.get("district_id")
        place = dict_data.get("place")
        mobile = dict_data.get("mobile")
        tel = dict_data.get("tel")
        email = dict_data.get("email")

        #2,校验参数
        if not all([title,receiver,province_id,city_id,district_id,place,mobile,tel,email]):
            return http.HttpResponseForbidden("参数不全")

        #3,数据入库
        address = Address.objects.get(id=address_id)
        address.title = title
        address.receiver = receiver
        address.province_id = province_id
        address.city_id = city_id
        address.district_id = district_id
        address.place = place
        address.mobile = mobile
        address.tel = tel
        address.email = email
        address.save()

        #4,返回响应
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email,
            "province_id": address.province_id,
            "city_id": address.city_id,
            "district_id": address.district_id
        }
        return http.JsonResponse({"code":RET.OK,"address":address_dict})

    def delete(self,request,address_id):

        #1,获取地址对象
        address = Address.objects.get(id=address_id)

        #2,修改地址的is_deleted属性,入库
        address.is_deleted = True
        address.save()

        #3,返回响应
        return http.JsonResponse({"code":RET.OK})

class AddressDefaultView(MyLoginRequiredMiXinView):
    def put(self,request,address_id):
        #1,入库
        request.user.default_address_id = address_id
        request.user.save()

        #2,返回
        return http.JsonResponse({"code":RET.OK})

class AddressTitleView(MyLoginRequiredMiXinView):
    def put(self,request,address_id):

        #1,获取参数
        title = json.loads(request.body.decode()).get("title")

        #2,为空校验参数
        if not title:
            return http.HttpResponseForbidden("参数不全")

        #3,数据入库
        ret = Address.objects.filter(id=address_id).update(title=title)
        if ret == 0:
            return http.HttpResponseForbidden("修改失败")

        #4,返回响应
        return http.JsonResponse({"code":RET.OK})

class PasswordChangeView(MyLoginRequiredMiXinView):
    def get(self,request):
        return render(request,'user_center_pass.html')

    def post(self,request):
        #1,获取参数
        old_pwd = request.POST.get("old_pwd")
        new_pwd = request.POST.get("new_pwd")
        new_cpwd = request.POST.get("new_cpwd")

        #2,校验参数
        #2.1为空校验
        if not all([old_pwd,new_pwd,new_cpwd]):
            return http.HttpResponseForbidden("参数不全")

        #2,2校验密码格式
        if not re.match(r'^[0-9A-Za-z]{8,20}$',old_pwd):
            return http.HttpResponseForbidden("旧密码格式有误")

        if not re.match(r'^[0-9A-Za-z]{8,20}$',new_pwd):
            return http.HttpResponseForbidden("旧密码格式有误")

        #2.3旧密码正确性
        if not request.user.check_password(old_pwd):
            return http.HttpResponseForbidden("旧密码不正确")

        #2.4两次新密码正确性
        if new_pwd != new_cpwd:
            return http.HttpResponseForbidden("两次新密码不一致")

        #3,数据入库
        request.user.set_password(new_pwd)
        request.user.save()

        #4,返回响应,清空session信息
        logout(request)
        response = redirect('/login')
        response.delete_cookie("username")
        return response