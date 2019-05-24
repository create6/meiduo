import re

from django.contrib.auth.backends import ModelBackend

from users.models import User

def get_user_by_account(username):
    try:
        if re.match(r'^1[3-9]\d{9}$', username):
            user = User.objects.get(mobile=username)
        else:
            user = User.objects.get(username=username)
    except User.DoesNotExist:
        return None
    else:
        return user

class MyBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None,**kwargs):

        #1,通过用户名或者手机号得到用户
        user = get_user_by_account(username)

        #2,返回
        return user





