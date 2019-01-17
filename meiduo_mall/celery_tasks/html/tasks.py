#coding:utf8
import os
from celery_tasks.main import app
from utils.goods import get_categories
from django.template import loader
from django.conf import settings

@app.task(name='generate_static_list_search_html')
def generate_static_list_search_html():
    """
    生成静态的商品列表页html文件
    """
    # 商品分类菜单
    categories = get_categories()

    # 渲染模板，生成静态html文件
    context = {
        'categories': categories,
    }

    # 1. 先加载模板
    template = loader.get_template('list.html')
    #2. 将数据传递给模板
    html_text = template.render(context)
    #3.设置路径
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'list.html')
    #4.写入
    with open(file_path, 'w') as f:
        f.write(html_text)