from itsdangerous import Serializer
from meiduo_mall import settings


#返回openid
def generic_open_id(openid):

    #1.创建序列化器
    s = Serializer(secret_key=settings.SECRET_KEY,expires_in=60*60)

    #2.对数据进行校验
    token=s.dumps({
        'openid':openid
    })

    #3.返回数据
    return token.decode()