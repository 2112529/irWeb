from bs4 import BeautifulSoup
import urllib.request
import xml.etree.ElementTree as ET

def get_news_pool(root, start, end):
    news_pool = []
    for i in range(start,end,-1):
        page_url = root
        try:
            response = urllib.request.urlopen(page_url)
        except Exception as e:
            print("-----%s: %s-----"%(type(e), page_url))
            continue
        
        html = response.read()
        #转为utf-8编码
        html = html.decode('utf-8')
        #print(html)
        soup = BeautifulSoup(html,"lxml") 
        #可以尝试直接找li标签
        div = soup.find('div', class_ = "focus-news-box")
        if div:
            li_elements = div.find_all('li')
        else:
            li_elements = []
        #print(li_elements)
        for li in li_elements:
            # 对每个<li>元素找到所有的<a>标签
            a_elements = li.find_all('a')
            # print(a_elements)
            #span_elements = li.find_all('span')
            # 现在您可以处理每个<li>中的<a>元素
            for i in range(len(a_elements)):
                #date_time = span_elements[i].string
                url = "https://www.sohu.com"+a_elements[i].get('href')
                title = a_elements[i].string
                news_info = [url,title]
                news_pool.append(news_info)
        #print(news_pool)
        return(news_pool)

def crawl_news(news_pool, doc_dir_path, doc_encoding):
    i = 1
    for news in news_pool:
        # print(news)
        try:
            response = urllib.request.urlopen(news[0])
        except Exception as e:
            print("-----%s: %s-----"%(type(e), news[0]))
            continue
        html = response.read()
        soup = BeautifulSoup(html,"lxml") 
        try:
             # 查找包含关键词的meta标签
            keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
            # 如果找到了标签，提取内容
            keywords = keywords_tag.get('content', '') if keywords_tag else ''

            # 查找包含描述的meta标签
            description_tag = soup.find('meta', attrs={'name': 'description'})
            # 如果找到了标签，提取内容
            description = description_tag.get('content', '') if description_tag else ''
        except Exception as e:
            print("-----%s: %s-----"%(type(e), news[0]))
            continue
        # print(keywords)
        # print(description)
        doc = ET.Element("doc")
        ET.SubElement(doc, "id").text = "%d"%(i)
        ET.SubElement(doc, "url").text = news[0]
        ET.SubElement(doc, "title").text = news[1]
        ET.SubElement(doc, "keywords").text = keywords
        ET.SubElement(doc, "description").text = description
        tree = ET.ElementTree(doc)

        file_path = doc_dir_path + "%d.xml" % i        
        tree.write(file_path, encoding = doc_encoding, xml_declaration = True)
        i += 1

    
if __name__ == '__main__':
    root = 'https://www.sohu.com/?pvid=b6a6473ea63069a1'
    news_pool = get_news_pool(root, 854, 849)
    crawl_news(news_pool, "Data/news/", "utf-8")
    print(' worm.py is done!')