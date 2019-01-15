from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView

from goods.models import SKU
from goods.serializers import HotSKUListSerializer

"""
表的设计 思想:
    1. 根据产品给的原型 尽量多的分析表的字段 (不要分析表和表之间的关系)
    2. 在一个安静的没有人打扰的环境中 分析表和表之间的关系(2个表和2个表去分析)
"""


class HomeAPIView(APIView):
    pass


"""
页面静态化  -- 提升用户体验 ,SEO

其实就是我们先把数据 查询出来,查询出来之后,将数据填充到模板中,
形式了html,将html写入到指定的文件

当用户访问的时候 ,直接访问 静态html


"""


"""
列表数据

一个是热销数据
列表数据

热销数据: 应该是到哪个分类去 获取哪个分类的热销数据

1. 获取分类id
2. 根据id获取数据  [SKU,SKU,SKU]
3. 将数据转化为字典(JSON数据)
4. 返回相应

GET      /goods/categories/(?P<category_id>\d+)/hotskus/

"""
from rest_framework.generics import ListAPIView
class HotSKUListAPIView(ListAPIView):

    # queryset = SKU.objects.filter(category_id=category_id).order_by('-sales')[:2]
    # queryset = SKU.objects.all()
    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id).order_by('-sales')[:2]


    serializer_class = HotSKUListSerializer