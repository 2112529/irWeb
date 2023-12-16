from django.shortcuts import render
from django.shortcuts import render,redirect
from django.http import HttpResponse

from App0 import models
from App0.models import NewsArticle,Knearest
from App0.search import NewsSearchEngine

def index(req):
    return HttpResponse('welcome to Django Test!')
def search(req):
    # 初始化空的查询结果和相关文章列表
    articles = None
    related_articles = []
    search_attempted = False

    if req.method == 'POST':
        search_attempted = True
        title = req.POST.get('title')

        # 尝试在数据库中搜索对应的文章
        try:
            articles = NewsArticle.objects.filter(title=title)

            # 如果找到匹配的文章
            if articles.exists():
                # 获取第一个匹配文章的 ID
                article_id = articles.first().id

                # 从 Knearest 表中获取与该文章相关的文章 ID
                try:
                    knearest = Knearest.objects.get(pk=article_id)
                    related_ids = [knearest.first, knearest.second, knearest.third, knearest.fourth, knearest.fifth]

                    # 根据相关文章的 ID 搜索 NewsArticle 表
                    related_articles = NewsArticle.objects.filter(id__in=related_ids)
                except Knearest.DoesNotExist:
                    related_articles = []

        except NewsArticle.DoesNotExist:
            articles = None

    return render(req, 'search.html', {
        'articles': articles,
        'related_articles': related_articles,
        'search_attempted': search_attempted
    })

def search_word(req):
     # 初始化空的查询结果和相关文章列表
    articles = None
    search_attempted = False

    if req.method == 'POST':
        search_attempted = True
        title = req.POST.get('title')
        # 尝试在数据库中搜索对应的文章
        try:
            search=NewsSearchEngine()
            search.parse_query(title)
            article_idlist=search.search(title)
            print(article_idlist)
            for id in article_idlist:
                articles=NewsArticle.objects.filter(id=id)
        except NewsArticle.DoesNotExist:
            articles = None

    return render(req, 'search_word.html', {
        'articles': articles,
        'search_attempted': search_attempted
    })
