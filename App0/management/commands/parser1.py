import os
import xml.etree.ElementTree as ET
from django.core.management.base import BaseCommand
from App0.models import NewsArticle1  # 替换为你的应用名称和模型
from django.utils.dateparse import parse_datetime
import jieba.analyse

class Command(BaseCommand):
    help = 'Parse XML files and store the data in the NewsArticle model'

    def parse_xml_file(self,file_path):
        tree = ET.parse(file_path)
        doc = tree.getroot()

        # 根据 XML 结构获取数据
        news_id = doc.find('id').text if doc.find('id') is not None else 0
        title = doc.find('title').text if doc.find('title') is not None else 'Untitled'
        url = doc.find('url').text if doc.find('url') is not None else 'No URL'
        pub_date = parse_datetime(doc.find('pub_date').text) if doc.find('pub_date') is not None else None
        content = doc.find('content').text if doc.find('content') is not None else 'No Content'
        keywords=doc.find('keywords').text if doc.find('keywords') is not None else 'No Keywords'
        snapshot = doc.find('snapshot').text if doc.find('snapshot') is not None else 'No Snapshot'

        # 获取 PageRank 分数
        # 获取并处理 PageRank 分数
        pagerank_text = doc.find('pagerank_score').text if doc.find('pagerank_score') is not None else '0.0'
        pagerank_text = pagerank_text.replace('(', '').replace(')', '').replace(',', '').strip()
        pagerank_score = float(pagerank_text)


        # 创建新的 NewsArticle1 对象
        NewsArticle1.objects.create(
            news_id=news_id,
            title=title,
            url=url,
            pub_date=pub_date,
            content=content,
            keywords=keywords,
            snapshot=snapshot,
            pagerank_score=pagerank_score
        )
        print("create success!")
            

    def process_xml_files(self, directory):
        NewsArticle1.objects.all().delete()

        for filename in os.listdir(directory):
            if filename.endswith(".xml"):
                file_path = os.path.join(directory, filename)
                print(file_path)
                self.parse_xml_file(file_path)

    def handle(self, *args, **kwargs):
        directory = 'News1/'  # 或者从kwargs获取
        self.process_xml_files(directory)
        self.stdout.write(self.style.SUCCESS('Successfully parsed XML files'))
