from django.shortcuts import render
from django.shortcuts import render,redirect
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required
import jieba.analyse
from App0 import models
from App0.models import NewsArticle,Knearest,SearchHistory,NewsArticle1
from App0.search import NewsSearchEngine

# 尝试使用机器学习的方式优化模型
from transformers import BertTokenizer, BertModel
import torch
import torch.nn as nn
# 初始化 BERT 分词器和模型
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')



# def index(req):
#     return HttpResponse('welcome to Django Test!')
@login_required
def search(request):
    articles = None
    related_articles = []
    search_attempted = False

    if request.method == 'POST':
        search_attempted = True
        title = request.POST.get('title')
        selected_categories = request.POST.getlist('category')
        # 记录搜索历史
        if request.user.is_authenticated:
            SearchHistory.objects.create(user=request.user, query=title)

        # 尝试在数据库中搜索对应的文章
        try:
            # 根据标题和选定的类型搜索文章
            articles_query = NewsArticle1.objects.filter(title__icontains=title)
            if selected_categories:
                articles_query = articles_query.filter(category__in=selected_categories)
            articles = articles_query.values('title', 'keywords', 'content', 'snapshot').distinct()

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
    
# @login_required
# def search_word(req):
#      # 初始化空的查询结果和相关文章列表
#     articles = []
#     sorted_articles=[]
#     search_attempted = False

#     if req.method == 'POST':
        
#         search_attempted = True
        
#         title = req.POST.get('title')
#         if req.user.is_authenticated:
#             SearchHistory.objects.create(user=req.user, query=title)
#         # 尝试在数据库中搜索对应的文章
#         try:
#             search=NewsSearchEngine()
#             article_idlist=search.search(title)
#             print(article_idlist)
#             for id in article_idlist:
#                 articles.append(NewsArticle1.objects.get(news_id=id))
#             sorted_articles = sorted(articles, key=lambda x: x.pagerank_score, reverse=True)
#         except NewsArticle1.DoesNotExist:
#             articles = None

#     return render(req, 'search_word.html', {
#         'articles': sorted_articles,
#         'search_attempted': search_attempted
#     })


def get_embedding(text):
    # 将文本编码为词索引
    inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
    # 获取文本的 BERT 嵌入
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1)


class FusionModule(nn.Module):
    def __init__(self, embedding_dim):
        super(FusionModule, self).__init__()
        self.fc = nn.Linear(2 * embedding_dim, embedding_dim)

    def forward(self, title_emb, history_emb):
        # 假设我们取历史嵌入的平均值
        avg_history_emb = torch.mean(history_emb, dim=1)
        combined = torch.cat((title_emb, avg_history_emb), dim=1)
        fused_embedding = self.fc(combined)
        return fused_embedding


@login_required
def search_word(req):
     # 初始化空的查询结果和相关文章列表
    articles = []
    sorted_articles=[]
    search_attempted = False
    if req.method == 'POST':
        
        search_attempted = True
        
        title = req.POST.get('title')
        title_embedding = get_embedding(title)  
        search_historys = SearchHistory.objects.filter(user_id=req.user.user_id).order_by('-timestamp').values_list('query', flat=True)
        search_history=''
        for history in search_historys:
            search_history +=history
        # 将文本转换为 BERT 可以理解的格式
        inputs = tokenizer(search_history, padding=True, truncation=True, return_tensors="pt")

        # 获取文本的嵌入表示
        with torch.no_grad():
            outputs = model(**inputs)
        # 可以使用 outputs.last_hidden_state 或 outputs.pooler_output
        search_history_embeddings = outputs.last_hidden_state

        if req.user.is_authenticated:
            SearchHistory.objects.create(user=req.user, query=title)

        
        doc_similarity_dict=[]
        # 初始化融合模块
        fusion_module = FusionModule(embedding_dim=title_embedding.size(1))

        # 融合
        fused_embedding = fusion_module(title_embedding, search_history_embeddings)

        # 计算与文档的相似度
        docs = NewsArticle1.objects.all()
        for doc in docs:
            doc_embedding = get_embedding(doc.title + doc.keywords) # 从模型中获取文档的嵌入
            doc_embedding = torch.tensor(doc_embedding) # 转换为 PyTorch Tensor

            # 计算余弦相似度
            cos_sim = nn.functional.cosine_similarity(fused_embedding, doc_embedding)

            # 将新闻 ID 和相似度存储到字典中
            similarity_dict = {'news_id': doc.news_id, 'similarity': cos_sim.item()}
            # 使用字典存储下来
            doc_similarity_dict.append(similarity_dict)
        sorted_articles = sorted(doc_similarity_dict, key=lambda x: x['similarity'], reverse=True)
        # 找出排名前五的文档
        top_articles = sorted_articles[:5]
        for article_id in top_articles:
            articles.append(NewsArticle1.objects.get(news_id=article_id['news_id']))
        sorted_articles = sorted(articles, key=lambda x: x.pagerank_score, reverse=True)

        
        # # 尝试在数据库中搜索对应的文章
        # try:
        #     search=NewsSearchEngine()
        #     article_idlist=search.search(title)
        #     print(article_idlist)
        #     for id in article_idlist:
        #         articles.append(NewsArticle1.objects.get(news_id=id))
        #     sorted_articles = sorted(articles, key=lambda x: x.pagerank_score, reverse=True)
        # except NewsArticle1.DoesNotExist:
        #     articles = None

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


from App0.models import UserInfo,SearchHistory
from collections import Counter


@login_required
def p_search(request):
    articles = []
    sorted_articles = []
    search_attempted = False
    print("---------------")

    if request.method == 'POST':
        search_attempted = True

        # 获取用户查询词
        title = request.POST.get('title')
        title = (title + ' ') * 5  # 重复五遍，并在每次重复后添加空格以分隔单词


        # 记录用户的搜索历史
        if request.user.is_authenticated:
            SearchHistory.objects.create(user=request.user, query=title)

        # 调整查询向量，基于用户特征
        gender =UserInfo.objects.get(user_id=request.user.user_id).gender
        occupation = UserInfo.objects.get(user_id=request.user.user_id).occupation

       # 为查询向量添加基于性别的关键词
        additional_terms = []
        if gender == 'Male':
            additional_terms.extend(['国家', '经济', '军队'])  # 示例关键词
        elif gender == 'Female':
            additional_terms.extend(['明星', '火锅', '大学'])  # 示例关键词

        # 如果用户是学生，添加相关关键词
        if occupation == 'Student':
            additional_terms.append('学生')

        # 根据历史搜索记录调整查询向量
        history_terms = SearchHistory.objects.filter(user_id=request.user.user_id).values_list('query', flat=True)
        for term in history_terms:
            additional_terms.extend(term.split())

        # 计算词频并选择前五个最频繁的词
        term_frequencies = Counter(additional_terms)
        top_terms = [term for term, _ in term_frequencies.most_common(5)]
        
        # 将核心关键词添加到查询词中
        for term in top_terms:
            title += ' ' + term

        # 执行搜索
        search = NewsSearchEngine()
        print(title)
        article_idlist = search.search(title)
        for id in article_idlist:
            articles.append(NewsArticle1.objects.get(news_id=id))

        sorted_articles = sorted(articles, key=lambda x: x.pagerank_score, reverse=True)

    return render(request, 'p_search.html', {
        'articles': sorted_articles,
        'search_attempted': search_attempted
    })


@login_required
def main(request):
    # 获取当前登录用户的ID
    user_id = request.user.user_id

    # 获取用户的最近搜索历史
    recent_searches = SearchHistory.objects.filter(user_id=user_id).order_by('-timestamp')[:5]

    # 提取关键词
    keywords = set()
    for search in recent_searches:
        for keyword in jieba.analyse.extract_tags(search.query):
            keywords.add(keyword)

    # 基于关键词推荐相关文章
    recommended_articles = []
    for keyword in keywords:
        articles = NewsArticle1.objects.filter(content__icontains=keyword)[:5]
        recommended_articles.extend(articles)

    return render(request, 'main.html', {'recommended_articles': recommended_articles})




