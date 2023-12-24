from django.shortcuts import render
from django.shortcuts import render,redirect
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required
import jieba.analyse
from App0 import models
from App0.models import NewsArticle,Knearest,SearchHistory,NewsArticle1
from App0.search import NewsSearchEngine

def index(req):
    return HttpResponse('welcome to Django Test!')
@login_required
def search(request):
    articles = None
    related_articles = []
    search_attempted = False

    if request.method == 'POST':
        search_attempted = True
        title = request.POST.get('title')

        # 记录搜索历史
        if request.user.is_authenticated:
            SearchHistory.objects.create(user=request.user, query=title)

        # 尝试在数据库中搜索对应的文章
        try:
            articles = NewsArticle1.objects.filter(title=title).values('title','keywords','content','snapshot').distinct()

            # 如果找到匹配的文章
            # if articles.exists():
            #     # 获取第一个匹配文章的 ID
            #     article_id = articles.first().id

            #     # 从 Knearest 表中获取与该文章相关的文章 ID
            #     try:
            #         knearest = Knearest.objects.get(pk=article_id)
            #         related_ids = [knearest.first, knearest.second, knearest.third, knearest.fourth, knearest.fifth]

            #         # 根据相关文章的 ID 搜索 NewsArticle 表
            #         related_articles = NewsArticle.objects.filter(id__in=related_ids).distinct()
            #     except Knearest.DoesNotExist:
            related_articles = []

        except NewsArticle.DoesNotExist:
            articles = None

    return render(request, 'search.html', {
        'articles': articles,
        'related_articles': related_articles,
        'search_attempted': search_attempted
    })
    
@login_required
def search_word(req):
     # 初始化空的查询结果和相关文章列表
    articles = []
    sorted_articles=[]
    search_attempted = False

    if req.method == 'POST':
        
        search_attempted = True
        
        title = req.POST.get('title')
        if req.user.is_authenticated:
            SearchHistory.objects.create(user=req.user, query=title)
        # 尝试在数据库中搜索对应的文章
        try:
            search=NewsSearchEngine()
            article_idlist=search.search(title)
            print(article_idlist)
            for id in article_idlist:
                articles.append(NewsArticle1.objects.get(news_id=id))
            sorted_articles = sorted(articles, key=lambda x: x.pagerank_score, reverse=True)
        except NewsArticle1.DoesNotExist:
            articles = None

    return render(req, 'search_word.html', {
        'articles': sorted_articles,
        'search_attempted': search_attempted
    })

@login_required
def wildcard_search(request):
    query=''
    if request.method == 'POST':
        query = request.POST.get('query', '')  # 获取 POST 请求中的查询参数
        if request.user.is_authenticated:
            SearchHistory.objects.create(user=request.user, query=query)
    search_engine = NewsSearchEngine()  # 创建 NewsSearchEngine 实例


    # 使用通配符查询处理
    # expanded_queries = search_engine.process_wild_query(query)
    results = search_engine.search_with_wildcard(query)

    # 格式化结果，这里假设 results 是一个包含文档ID的列表
    formatted_results = []
    sorted_articles = []
    for doc_id in results:
        # 根据文档ID获取文档详情，这里需要根据您的实际数据模型来实现
        document = NewsArticle1.objects.get(news_id=doc_id)
        formatted_results.append(document)
        sorted_articles = sorted(formatted_results, key=lambda x: x.pagerank_score, reverse=True)
        # pass

    return render(request, 'search_wildcard.html', {'articles': sorted_articles})

@login_required
def p_search(request):
    articles = []
    sorted_articles = []
    search_attempted = False

    if request.method == 'POST':
        search_attempted = True

        # 获取用户查询词
        title = request.POST.get('title')

        # 记录用户的搜索历史
        if request.user.is_authenticated:
            SearchHistory.objects.create(user=request.user, query=title)

        # 调整查询向量，基于用户特征
        gender = request.user.gender
        occupation = request.user.occupation  # 假设有这个字段

        # 为查询向量添加基于性别的关键词
        if gender == 'Male':
            title += ' 国家 经济 军队'  # 示例关键词
        elif gender == 'Female':
            title += ' 明星 火锅 大学'  # 示例关键词

        # 如果用户是学生，添加相关关键词
        if occupation == 'Student':
            title += ' 学生'

        # 根据历史搜索记录调整查询向量
        history_terms = request.user.search_history.all().values_list('query', flat=True)
        for term in history_terms:
            title += ' ' + term

        # 执行搜索
        search = NewsSearchEngine()
        article_idlist = search.search(title)
        for id in article_idlist:
            articles.append(NewsArticle1.objects.get(news_id=id))

        sorted_articles = sorted(articles, key=lambda x: x.pagerank_score, reverse=True)

    return render(request, 'search_word.html', {
        'articles': sorted_articles,
        'search_attempted': search_attempted
    })


