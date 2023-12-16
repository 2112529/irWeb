import os
import xml.etree.ElementTree as ET
from django.core.management.base import BaseCommand
from App0.models import NewsArticle  # 替换为你的应用名称和模型
from django.utils.dateparse import parse_datetime

class Command(BaseCommand):
    help = 'Parse XML files and store the data in the NewsArticle model'

    def parse_xml_file(self, file_path):
        tree = ET.parse(file_path)
        doc = tree.getroot()

        title = doc.find('title').text if doc.find('title') is not None else 'Untitled'
        # print(title)
        author = doc.find('author').text if doc.find('author') is not None else 'Unknown'
        pub_date = parse_datetime(doc.find('pub_date').text) if doc.find('pub_date') is not None else "2023-10-10"
        content = doc.find('description').text if doc.find('description') is not None else 'None'
        keywords = doc.find('keywords').text if doc.find('keywords') is not None else 'keywords'


        # 创建新的 NewsArticle 对象
        NewsArticle.objects.create(
            title=title,
            author=author,
            pub_date=pub_date,
            content=content,
            keywords=keywords
        )
        print("create success!")
            

    def process_xml_files(self, directory):
        NewsArticle.objects.all().delete()

        for filename in os.listdir(directory):
            if filename.endswith(".xml"):
                file_path = os.path.join(directory, filename)
                print(file_path)
                self.parse_xml_file(file_path)

    def handle(self, *args, **kwargs):
        directory = 'News/'  # 或者从kwargs获取
        self.process_xml_files(directory)
        self.stdout.write(self.style.SUCCESS('Successfully parsed XML files'))
