from itsdangerous import Serializer, BadSignature
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



def check_access_token(access_token):
    #创建序列化器
    s=Serializer(secret_key=settings.SECRET_KEY,exires_in=60*60)
    #对数据进行loads()操作
    try:
        data=s.loads(access_token)
    except BadSignature:
        return None
    #返回openid
    return data['openid']