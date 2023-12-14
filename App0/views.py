from django.shortcuts import render
from django.shortcuts import render,redirect
from django.http import HttpResponse
# Create your views here.
from App0 import models
from App0.models import NewsArticle

def index(req):
    return HttpResponse('welcome to Django Test!')
def search(req):
    # 初始化一个空的查询结果
    articles = None
    search_attempted = False  # 新增变量

    # 检查是否为POST请求
    if req.method == 'POST':
        search_attempted = True  # 如果是POST请求，设置为True
        # 从表单中获取标题
        title = req.POST.get('title')
        # 在数据库中搜索对应的文章
        try:
            articles = NewsArticle.objects.filter(title=title)
        except NewsArticle.DoesNotExist:
            # 如果文章不存在，则返回None
            articles = None

    # 将结果（无论是文章对象还是None）传递给模板
    return render(req, 'search.html', {'articles': articles, 'search_attempted': search_attempted})
