from itsdangerous import TimedJSONWebSignatureSerializer as TJSWSSerializer

#1,加密openid
def generate_sign_openid(openid):

    #1,创建TJSWSSerializer对象
    serializer = TJSWSSerializer(secret_key="oauth",expires_in=300)

    #2,加密openid
    sign_openid = serializer.dumps({"openid":openid})

    #3,返回结果
    return sign_openid.decode()

#2,解密openid
def decode_sign_openid(data):
    # 1,创建TJSWSSerializer对象
    serializer = TJSWSSerializer(secret_key="oauth", expires_in=300)

    # 2,加密openid
    try:
        data_dict = serializer.loads(data)
    except Exception as e:
        return None

    # 3,返回结果
    return data_dict.get("openid")