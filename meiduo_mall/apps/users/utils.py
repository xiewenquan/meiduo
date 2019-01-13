from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,BadSignature
from meiduo_mall import settings


def generic_verify_url(user_id):

    # 1. 创建序列化器
    s = Serializer(secret_key=settings.SECRET_KEY,expires_in=3600)
    #2. 组织数据
    data = {
        'id':user_id
    }
    #3. 对数据加密
    token = s.dumps(data)
    #4. 拼接url

    return 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token.decode()


def check_token(token):

    #1. 创建序列化器
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
    #2. 解析数据
    try:
        result = s.loads(token)
    except BadSignature:
        return None

    #3.返回user_id
    return result.get('id')