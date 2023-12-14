from os import listdir
import xml.etree.ElementTree as ET
import jieba
import jieba.analyse
import sqlite3
import configparser
from datetime import *
import math

import pandas as pd
import numpy as np

from sklearn.metrics import pairwise_distances

class recommend:
    stop_words = set()
    k_nearest = []
    
    config_path = ''
    config_encoding = ''
    
    doc_dir_path = ''
    doc_encoding = ''
    stop_words_path = ''
    stop_words_encoding = ''
    idf_path = ''
    db_path = ''
    
    def __init__(self):
        

        self.doc_dir_path = "Data/news/"
        self.doc_encoding = "utf-8"
        self.stop_words_path = "Data/stop_words.txt"
        self.stop_words_encoding = "utf-8"
        self.idf_path = "Data/idf.txt"
        self.db_path = "Data/ir.db"

        f = open(self.stop_words_path, encoding = self.stop_words_encoding)
        words = f.read()
        self.stop_words = set(words.split('\n'))
    
    def write_k_nearest_matrix_to_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''DROP TABLE IF EXISTS knearest''')
        c.execute('''CREATE TABLE knearest
                     (id INTEGER PRIMARY KEY, first INTEGER, second INTEGER,
                     third INTEGER, fourth INTEGER, fifth INTEGER)''')

        for docid, doclist in self.k_nearest:
            c.execute("INSERT INTO knearest VALUES (?, ?, ?, ?, ?, ?)", tuple([docid] + doclist))

        conn.commit()
        conn.close()
    
    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False
            
    
    def construct_dt_matrix(self, files, topK = 200):
        jieba.analyse.set_stop_words(self.stop_words_path)
        jieba.analyse.set_idf_path(self.idf_path)
        M = len(files)#file nums
        N = 1
        terms = {}
        dt = []
        for file in files:
            root = ET.parse(self.doc_dir_path + file).getroot()
            title = root.find('title').text
            discription=root.find('description').text
            keywords=root.find('keywords').text
            if title==None : 
                title = ' '
            if discription==None : 
                discription = ' '
            if keywords==None :
                keywords = ' '
            docid = int(root.find('id').text)
            tags = jieba.analyse.extract_tags(title + '。' + discription+'。' + keywords, topK=topK, withWeight=True)
            #tags = jieba.analyse.extract_tags(title, topK=topK, withWeight=True)
            cleaned_dict = {}
            for word, tfidf in tags:
                word = word.strip().lower()
                if word == '' or self.is_number(word):
                    continue
                cleaned_dict[word] = tfidf
                if word not in terms:
                    terms[word] = N
                    N += 1
            dt.append([docid, cleaned_dict])
        dt_matrix = [[0 for i in range(N)] for j in range(M)]
        i =0
        for docid, t_tfidf in dt:
            dt_matrix[i][0] = docid
            for term, tfidf in t_tfidf.items():
                dt_matrix[i][terms[term]] = tfidf
            i += 1

        dt_matrix = pd.DataFrame(dt_matrix)
        dt_matrix.index = dt_matrix[0]
        print('dt_matrix shape:(%d %d)'%(dt_matrix.shape))
        return dt_matrix
        
    def construct_k_nearest_matrix(self, dt_matrix, k):
        tmp = np.array(1 - pairwise_distances(dt_matrix[dt_matrix.columns[1:]], metric = "cosine"))
        similarity_matrix = pd.DataFrame(tmp, index = dt_matrix.index.tolist(), columns = dt_matrix.index.tolist())
        for i in similarity_matrix.index:
            tmp = [int(i),[]]
            j = 0
            while j < k:
                max_col = similarity_matrix.loc[i].idxmax()
                similarity_matrix.loc[i][max_col] =  -1
                if max_col != i:
                    tmp[1].append(int(max_col)) #max column name
                    j += 1
            self.k_nearest.append(tmp)
    
    def gen_idf_file(self):
        files = listdir(self.doc_dir_path)
        n = float(len(files))
        idf = {}#文档频率的倒数
        for file in files:
            root = ET.parse(self.doc_dir_path + file).getroot()
            title = root.find('title').text if root.find('title') is not None else ''
            discription = root.find('description').text if root.find('description') is not None else ''
            keywords = root.find('keywords').text if root.find('keywords') is not None else ''
            # print("")
            # print("title:",title)
            # print("discription:",discription)
            # print('keywords:',keywords)
            if title==None : 
                title = ' '
            if discription==None : 
                discription = ' '
            if keywords==None :
                keywords = ' '
            seg_list = jieba.lcut(title + '。' + discription +'。' + keywords, cut_all=False)
            # seg_list = jieba.lcut(title + '。' + discription , cut_all=False)

            seg_list = set(seg_list) - self.stop_words
            for word in seg_list:
                word = word.strip().lower()
                if word == '' or self.is_number(word):
                    continue
                if word not in idf:
                    idf[word] = 1
                else:
                    idf[word] = idf[word] + 1
        idf_file = open(self.idf_path, 'w', encoding = 'utf-8')
        for word, df in idf.items():
            idf_file.write('%s %.9f\n'%(word, math.log(n / df)))
        idf_file.close()
        
    def find_k_nearest(self, k, topK):
        self.gen_idf_file()
        files = listdir(self.doc_dir_path)
        dt_matrix = self.construct_dt_matrix(files, topK)
        self.construct_k_nearest_matrix(dt_matrix, k)
        self.write_k_nearest_matrix_to_db()
        
if __name__ == "__main__":
    print('-----start time: %s-----'%(datetime.today()))
    rm = recommend()
    rm.find_k_nearest(5, 25)
    print('-----finish time: %s-----'%(datetime.today()))