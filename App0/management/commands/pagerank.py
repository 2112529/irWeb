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

    def assign_linked_articles(self):
        # 获取所有文章并按 news_id 排序
        all_articles = NewsArticle1.objects.all().order_by('news_id')

        # 计算总文章数量
        total_articles = len(all_articles)

        # 遍历每篇文章
        for index, article in enumerate(all_articles):
            # 根据 news_id 计算要链接的文章数量
            # 例如，对于前10%的文章，我们可以链接最多10篇文章，以此类推
            max_links = max(1, 10 - (index * 10 // total_articles))

            # 从所有文章中随机选择要链接的文章
            linked_articles = random.sample(list(all_articles), min(max_links, total_articles))

            # 确保不要链接到文章自身
            linked_articles = [linked_article for linked_article in linked_articles if linked_article != article]

            # 设置 linked_articles 字段
            article.linked_articles.set(linked_articles)

            # 保存更改
            article.save()
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
        # self.assign_linked_articles()
        self.calculate_pagerank()
        
