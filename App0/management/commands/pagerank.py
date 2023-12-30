from django.core.management.base import BaseCommand
from App0.models import NewsArticle1
import random
import networkx as nx

class Command(BaseCommand):
    help = 'Process and de-duplicate news articles'

    def singlenews(self):
        # 使用集合来跟踪已处理的 news_id
        processed_titles = set()
        # 获取所有文章对象
        all_articles = NewsArticle1.objects.all()
        # 遍历所有文章
        for article in all_articles:
            # 检查 news_id 是否已处理
            if article.title in processed_titles:
                # 删除数据库中的文章
                article.delete()
                self.stdout.write(self.style.WARNING(f'Duplicate article found and deleted: {article.title}'))
                continue
            # 在这里执行你想要的处理，例如打印、修改或其他操作
            # 示例：打印文章标题
            self.stdout.write(self.style.SUCCESS(f'Processing article: {article.title}'))
            # 将当前文章的 news_id 添加到已处理集合中
            processed_titles.add(article.title)
        # 完成处理后的信息
        self.stdout.write(self.style.SUCCESS('Finished processing articles'))

    
    def calculate_pagerank(self):
        # 创建一个有向图
        G = nx.DiGraph()

        # 添加节点
        for article in NewsArticle1.objects.all():
            G.add_node(article.id)

        # 添加边（文章之间的链接）
        for article in NewsArticle1.objects.all():
            linked_articles = article.linked_articles.all()
            for linked_article in linked_articles:
                G.add_edge(article.id, linked_article.id)

        # 计算 PageRank
        pagerank_scores = nx.pagerank(G)

        # 更新每篇文章的 pagerank_score
        for article in NewsArticle1.objects.all():
            article.pagerank_score = pagerank_scores.get(article.id, 0)
            article.save()
    def handle(self, *args, **kwargs):
        # self.singlenews()
        self.calculate_pagerank()
        
