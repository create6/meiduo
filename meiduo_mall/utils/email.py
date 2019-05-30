from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as TJSWSerializer

#1,生成加密的url链接地址
from users.models import User


def generate_verify_url(user):

    #1,创建数据信息
    dict_data = {"user_id":user.id, "email":user.email}

    #2,创建TJSWSerializer对象
    serializer = TJSWSerializer(secret_key=settings.SECRET_KEY,expires_in=60*30)

    #3,加密
    token = serializer.dumps(dict_data)

    #4,拼接链接
    verify_url = "%s?token=%s"%(settings.EMAIL_VERIFY_URL,token.decode())

    #5,返回
    return verify_url


#2,加密token
def decode_token(token):

    #1,创建TJSWSerializer对象
    serializer = TJSWSerializer(secret_key=settings.SECRET_KEY, expires_in=60 * 30)

    #2,解密数据
    try:
        dict_data = serializer.loads(token)

        user_id = dict_data.get("user_id")

        user =  User.objects.get(id=user_id)

    except Exception:
        return None

    #3,返回user
    return user