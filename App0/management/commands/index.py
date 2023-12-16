from os import listdir
import xml.etree.ElementTree as ET
import jieba
import sqlite3
from App0.models import Postings
from django.core.management.base import BaseCommand

class Doc:
    docid = 0
    tf = 0
    ld = 0
    def __init__(self, docid, tf, ld):
        self.docid = docid
        self.tf = tf
        self.ld = ld
    def __repr__(self):
        return(str(self.docid) + '\t'  + '\t' + str(self.tf) + '\t' + str(self.ld))
    def __str__(self):
        return(str(self.docid) + '\t'  + '\t' + str(self.tf) + '\t' + str(self.ld))

class IndexModule:
    stop_words = set()
    postings_lists = {}
    
    stop_words_path = "stop_words.txt"
    stop_words_encoding = "utf-8"
    
    def __init__(self,stop_words_path,stop_words_encoding):
        self.stop_words_path = stop_words_path
        self.stop_words_encoding = stop_words_encoding
        f = open(stop_words_path, encoding = stop_words_encoding)
        words = f.read()
        self.stop_words = set(words.split('\n'))

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False
        
    def clean_list(self, seg_list):
        cleaned_dict = {}
        n = 0
        for i in seg_list:
            i = i.strip().lower()
            if i != '' and not self.is_number(i) and i not in self.stop_words:
                n = n + 1
                if i in cleaned_dict:
                    cleaned_dict[i] = cleaned_dict[i] + 1
                else:
                    cleaned_dict[i] = 1
        return n, cleaned_dict
    
    def write_postings_to_db(self, postings_lists):
        # 清空现有数据
        Postings.objects.all().delete()

        # 插入新数据
        for key, value in postings_lists.items():
            doc_list = '\n'.join(map(str, value[1]))
            posting = Postings(term=key, df=value[0], docs=doc_list)
            posting.save()
    
    def construct_postings_lists(self):
        doc_dir_path="News/"
        files = listdir(doc_dir_path)
        AVG_L = 0
        for file in files:
            root = ET.parse(doc_dir_path + file).getroot()
            title=' '
            discription=' '
            keywords=' '
            if (root.find('title').text):
                title=root.find('title').text
            if(root.find('keywords').text):
                keywords=root.find('keywords').text
            if(root.find('description').text):
                discription=root.find('description').text
            docid = int(root.find('id').text)
            seg_list = jieba.lcut(title + '。' + discription+'。'+keywords, cut_all=False)
            
            ld, cleaned_dict = self.clean_list(seg_list)
            
            AVG_L = AVG_L + ld
            
            for key, value in cleaned_dict.items():
                d = Doc(docid, value, ld)
                if key in self.postings_lists:
                    self.postings_lists[key][0] = self.postings_lists[key][0] + 1 # df++
                    self.postings_lists[key][1].append(d)
                else:
                    self.postings_lists[key] = [1, [d]] # [df, [Doc]]
        AVG_L = AVG_L / len(files)
        self.write_postings_to_db(self.postings_lists)

class Command(BaseCommand):
    help = 'Constructs postings lists from XML data and writes to the database'

    def handle(self, *args, **options):
        im = IndexModule("stop_words.txt", "utf-8")
        im.construct_postings_lists()
        self.stdout.write(self.style.SUCCESS('Successfully constructed postings lists'))