import os
import xml.etree.ElementTree as ET
import sys
sys.path.append("..")
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'irWeb.settings')
django.setup()

from App0.models import NewsArticle  # 导入模型



def parse_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    for article in root.findall('article'):  # 假设每篇文章是 <article> 元素
        title = article.find('title').text
        author = article.find('author').text
        pub_date = article.find('pub_date').text  # 需要解析成适当的日期时间格式
        content = article.find('content').text
        keywords = article.find('keywords').text

        # 将提取的数据存储到 Django 模型中
        NewsArticle.objects.create(
            title=title,
            author=author,
            pub_date=pub_date,  # 确保这是一个 datetime 对象
            content=content,
            keywords=keywords
        )

def process_xml_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".xml"):
            file_path = os.path.join(directory, filename)
            print(file_path)
            parse_xml_file(file_path)
            

process_xml_files("/News/")
