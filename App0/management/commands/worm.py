from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
import urllib.request
import xml.etree.ElementTree as ET

# 动态爬取网页
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Command(BaseCommand):
    help = 'Crawls news from a given website and saves data as XML'


    def get_news_pool(self, root, start, end,count):
        news_pool = []
        for i in range(start,end,-1):
            page_url = root
            try:
                response = urllib.request.urlopen(page_url)
            except Exception as e:
                print("-----%s: %s-----"%(type(e), page_url))
                continue
            
            html = response.read()
            html = html.decode('utf-8')
            soup = BeautifulSoup(html,"lxml") 
            # div = soup.find('div', class_ = "focus-news-box")
            divs = soup.find_all('div', class_=['con'])
            print(divs)

            for div in divs:
                # 对每个单独的 div 元素使用 find_all 方法来查找所有的 li 元素
                li_elements = div.find_all('li')
                for li in li_elements:
                    a_elements = li.find_all('a')
                    for i in range(len(a_elements)):
                        href=a_elements[i].get('href')
                        if href.startswith('http') or href.startswith('//www'):
                            if href.startswith('//'):
                                href = "https:" + href
                            else:
                                url = href
                        else:
                            url = "https://www.sohu.com" + href
                        title = a_elements[i].string
                        news_info = [url,title]
                        news_pool.append(news_info)
            return(news_pool)

    def crawl_news(self, news_pool, doc_dir_path, doc_encoding):
        i = 242
        for news in news_pool:
            try:
                response = urllib.request.urlopen(news[0])
            except Exception as e:
                print("-----%s: %s-----" % (type(e), news[0]))
                continue
            html = response.read()
            soup = BeautifulSoup(html, "lxml")

            try:
                keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
                keywords = keywords_tag.get('content', '') if keywords_tag else ''
                description_tag = soup.find('meta', attrs={'name': 'description'})
                description = description_tag.get('content', '') if description_tag else ''
            except Exception as e:
                print("-----%s: %s-----" % (type(e), news[0]))
                continue
            
            doc = ET.Element("doc")
            ET.SubElement(doc, "id").text = str(i)
            ET.SubElement(doc, "url").text = news[0]
            ET.SubElement(doc, "title").text = news[1]
            ET.SubElement(doc, "keywords").text = keywords
            ET.SubElement(doc, "description").text = description
            tree = ET.ElementTree(doc)

            file_path = doc_dir_path + "%d.xml" % i        
            tree.write(file_path, encoding=doc_encoding, xml_declaration=True)
            i += 1

    def handle(self, *args, **options):
        root = 'https://xczx.cctv.com/index.shtml?spm=C88965.P72990804435.Ewq1d7wTU5C6.2'
        news_pool = self.get_news_pool(root, 854, 853,100)
        self.crawl_news(news_pool, "News/", "utf-8")
        self.stdout.write(self.style.SUCCESS('Successfully crawled news'))
