from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
import urllib.request
import requests
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
            divs = soup.find_all('div', class_ = "list16")
            divs.append(soup.find('div', class_ = "focus-news-box"))
            for div in divs:
                print(div)
                if div:
                    li_elements = div.find_all('li')
                else:
                    li_elements = []
                #print(li_elements)
                for li in li_elements:
                    # 对每个<li>元素找到所有的<a>标签
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
                        # title_div=a_elements[i].find('div',class_='text-info')
                        # title = title_div.string.strip() if title_div and title_div.string else ' '
                        title = a_elements[i].string
                        news_info = [url,title]
                        news_pool.append(news_info)
            print(news_pool)
            return(news_pool)

            # for div in divs:
            #     # 对每个单独的 div 元素使用 find_all 方法来查找所有的 li 元素
            #     li_elements = div.find_all('li')
            #     for li in li_elements:
            #         a_elements = li.find_all('a')
            #         for i in range(len(a_elements)):
            #             href=a_elements[i].get('href')
            #             if href.startswith('http') or href.startswith('//www'):
            #                 if href.startswith('//'):
            #                     href = "https:" + href
            #                 else:
            #                     url = href
            #             else:
            #                 url = "https://www.sohu.com" + href
            #             title = a_elements[i].string
            #             news_info = [url,title]
            #             news_pool.append(news_info)
            # print(news_pool)
            # return(news_pool)

    def crawl_news(self, news_pool, doc_dir_path, doc_encoding):
        i = 183
        for news in news_pool:
            print(news)
            try:
                response = urllib.request.urlopen(news[0])
            except Exception as e:
                print("-----%s: %s-----" % (type(e), news[0]))
                continue
            html = response.read()
            soup = BeautifulSoup(html, "lxml")
            try:
                div=soup.find('div',class_='left main')
                paragraphs = div.find_all('p')
                # 排除最后两个 <p> 标签
                content = ' '.join(p.get_text().strip() for p in paragraphs[:-2])

                # content = ' '.join(p.get_text().strip() for p in soup.find_all('p'))
                article_info=soup.find('div', class_ = "article-info")
                pub_date=article_info.find('span',class_="time").text
                # 提取网页快照（例如前几个段落）
                snapshot = ' '.join(p.get_text() for p in soup.find_all('p')[1:3])
                pagerank_score=0.0,  # 初始设置为0，稍后计算
                # 获取所有可以链接到 的文章
                linked_articles = []
                # outnum=0
        
                # for item in div.find_all('allsee-item'):
                #     outnum+=1
                #     print(item)
                #     link=item.find('a')
                #     href = link.get('href')
                #     if href.startswith('http') or href.startswith('//www'):
                #         if href.startswith('//'):
                #             href = "https:" + href
                #         else:
                #             url = href
                #     else:
                #         url = "https://www.sohu.com" + href
                    
                #     linked_articles.append(href)
                # linked_articles 需要在所有文章都保存后处理
            except Exception as e:
                print("-----%s: %s-----" % (type(e), news[0]))
                continue
            
            doc = ET.Element("doc")
            ET.SubElement(doc, "id").text = str(i)
            ET.SubElement(doc, "url").text = news[0]
            ET.SubElement(doc, "title").text = news[1]
            ET.SubElement(doc,"pub_date").text = pub_date
            # ET.SubElement(doc, "keywords").text = keywords
            ET.SubElement(doc, "content").text = content
            ET.SubElement(doc, "snapshot").text = snapshot
            ET.SubElement(doc, "pagerank_score").text = str(pagerank_score)
            ET.SubElement(doc, "linked_articles").text = ",".join(linked_articles)
            tree = ET.ElementTree(doc)

            file_path = doc_dir_path + "%d.xml" % i        
            tree.write(file_path, encoding=doc_encoding, xml_declaration=True)
            i += 1

    def handle(self, *args, **options):
        root = 'https://www.sohu.com/?pvid=b6a6473ea63069a1'
        news_pool = self.get_news_pool(root, 854, 853,100)
        # while(1):
        #     pass
        self.crawl_news(news_pool, "News1/", "utf-8")
        self.stdout.write(self.style.SUCCESS('Successfully crawled news'))
