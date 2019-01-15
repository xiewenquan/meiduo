from django.core.files.storage import Storage
from meiduo_mall import settings
from django.utils.deconstruct import deconstructible
from fdfs_client.client import Fdfs_client

#1. 您的自定义存储系统必须是以下子类 django.core.files.storage.Storage：


#4. 您的存储类必须是可解构的， 以便在迁移中的字段上使用时可以对其进行序列化。
# 只要您的字段具有可自行序列化的参数，
# 就可以使用 django.utils.deconstruct.deconstructible类装饰器
# （这就是Django在FileSystemStorage上使用的）。
@deconstructible
class MyStorage(Storage):
    #2. Django必须能够在没有任何参数的情况下实例化您的存储系统。
    # 这意味着任何设置都应该来自django.conf.settings：
    # def __init__(self, option=None):
    #     if not option:
    #         option = settings.CUSTOM_STORAGE_OPTIONS
    #     ...
    #3. 您的存储类必须实现_open()和_save() 方法,
    #   以及适用于您的存储类的任何其他方法。
    #因为我们的 Fdfs 是通过http来获取图片的,所以不需要打开方法
    def _open(self, name, mode='rb'):
        pass


    def _save(self, name, content, max_length=None):
        #1. 创建Fdfs的客户端，让客户端加载配置文件
        client=Fdfs_client('utils/fastdfs/client.conf')
        #2. 获取上传的文件
        file_data=content.read()
        #3. 上传图片，并获取　返回内容
        result=client.upload_by_buffer(file_data)
        #4. 根据返回内容，获取remote file_id
        if result.get('Status')=='Upload successed.':
            file_id=result.get('Remote file_id')
        else:
            raise Exception("上传失败")
        return file_id

    def exists(self, name):
        return False

    def url(self, name):

        return 'http:192.168.100.128:8888/'+name