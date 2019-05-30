from django.contrib.auth.backends import ModelBackend
import re
from users.models import User
class MyAuthenticateBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            #1,先判断username是否是手机号
            if re.match(r'^1[3-9]\d{9}$',username):
                user =  User.objects.get(mobile=username)
            else:
                #2,然后在通过用户名查询,用户
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        else:
            #3,校验密码
            if not user.check_password(password): return None
            return user