from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
import urllib.request
import xml.etree.ElementTree as ET

class Command(BaseCommand):
    help = 'Crawls news from a given website and saves data as XML'

    def get_news_pool(self, root, start, end,count):
        nav_news_pool = []
        nav_newscount=0
        for i in range(start, end, -1):
            page_url = root
            try:
                response = urllib.request.urlopen(page_url)
            except Exception as e:
                print("-----%s: %s-----" % (type(e), page_url))
                continue
            
            html = response.read()
            html = html.decode('utf-8')
            soup = BeautifulSoup(html, "lxml")
            div = soup.find('div', class_="colum_wrapper_13292")
            print(div)
            son_divs = div.find_all('div', class_="con")
            print(con)

            for son_div in son_divs:
                a_elements = son_div.find_all('a')
                for a in a_elements:
                    url = a.get('href')
                    title = a.string
                    nav_news_info = [url, title]
                    nav_news_pool.append(nav_news_info)
                    nav_newscount+=1
            # print(nav_newscount) 42
            # 获取导航信息结束，准备获取真正的新闻
            # print(nav_news_pool)

            news_pool = []
            newscount=0
            # print(Finace)
            # 处理财经类型的导航栏新闻---需要动态爬取网页
            
            Finace = []

            for nav_news in nav_news_pool:
                if nav_news[1] == ' 宏观 ':
                    Finace.append(nav_news)
                if nav_news[1] == ' 理财 ':
                    Finace.append(nav_news)



            for nav_news_info in Finace:
                nav_url=nav_news_info[0]
                print(nav_url)
                try:
                    response = urllib.request.urlopen(nav_url)
                except Exception as e:
                    print("-----%s: %s-----" % (type(e), nav_url))
                    continue
                html = response.read()
                # print(html)
                html = html.decode('utf-8')
                soup = BeautifulSoup(html, "lxml")
                div = soup.find('div', class_="left-feed")
                print(div)
                son_div=div.find("div",class_="CompTPLFeed")
                print(son_div)
                target_div = div.find('div', class_="cbd-recommend", attrs={"data-v-ed251ea6": True})
                print(target_div)
                for son_div in target_div:
                    a_elements = son_div.find_all('a')
                    for a in a_elements:
                        url = "https://www.sohu.com" + a.get('href')
                        title_div=a.find('div', class_="item-text-content-title")
                        title = title_div.string
                        news_info = [url, title]
                        news_pool.append(news_info)
                        newscount+=1
                    if newscount>count:break
            # 处理第一种类型的导航栏新闻

        return news_pool

    def crawl_news(self, news_pool, doc_dir_path, doc_encoding):
        i = 1
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
        root = 'https://news.cctv.com/'
        news_pool = self.get_news_pool(root, 854, 853,100)
        self.crawl_news(news_pool, "News/", "utf-8")
        self.stdout.write(self.style.SUCCESS('Successfully crawled news'))
