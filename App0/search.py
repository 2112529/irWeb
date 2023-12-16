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


class NewsSearchEngine:
    def __init__(self):
        self.stop_words_path = "stop_words.txt"
        self.stop_words_encoding = "utf-8"
        self.idf_path = "idf.txt"
        self.terms={}
        self.dt_matrix = []


    def construct_dt_matrix(self, files, topK = 200):
        jieba.analyse.set_stop_words(self.stop_words_path)
        jieba.analyse.set_idf_path(self.idf_path)
        M = len(files)#file nums
        N = 1
        #  self.terms = {}
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
                if word not in  self.terms:
                    self.terms[word] = N
                    N += 1
            dt.append([docid, cleaned_dict])
        dt_matrix = [[0 for i in range(N)] for j in range(M)]
        i =0
        for docid, t_tfidf in dt:
            dt_matrix[i][0] = docid
            for term, tfidf in t_tfidf.items():
                dt_matrix[i][ self.terms[term]] = tfidf
            i += 1

        dt_matrix = pd.DataFrame(dt_matrix)
        dt_matrix.index = dt_matrix[0]
        print('dt_matrix shape:(%d %d)'%(dt_matrix.shape))
        self.dt_matrix = dt_matrix
        return dt_matrix


    def process_query(self, query):
        # 分词
        query_words = list(jieba.cut(query))
        
        # 计算 TF
        tf_query = {}
        for word in query_words:
            word = word.strip().lower()
            if word in self.terms and word != '' and not self.is_number(word):
                tf_query[word] = tf_query.get(word, 0) + 1

        # 将查询转换为向量
        query_vector = [0] * len( self.terms)
        for word, freq in tf_query.items():
            index =  self.terms.get(word)
            if index is not None:
                query_vector[index] = freq

        return query_vector


    def search(self, query):
        query_vector = self.process_query(query, self. self.terms)
        results = []
        for i, row in self.dt_matrix.iterrows():
            doc_vector = row[1:]  # 跳过文档ID
            similarity = self.calculate_similarity(query_vector, doc_vector)
            results.append((row[0], similarity))  # row[0] 是文档ID
        results.sort(key=lambda x: x[1], reverse=True)  # 按相似度排序
        return results


    def calculate_similarity(self, vec1, vec2):
        # 计算两个向量的点积
        dot_product = 0
        for word, value in vec1.items():
            if word in vec2:
                dot_product += value * vec2[word]

        # 计算两个向量的模
        magnitude1 = math.sqrt(sum([x**2 for x in vec1.values()]))
        magnitude2 = math.sqrt(sum([x**2 for x in vec2.values()]))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0

        # 计算余弦相似度
        cosine_similarity = dot_product / (magnitude1 * magnitude2)
        return cosine_similarity

# 使用
    # def query(self,query):
    #     engine = NewsSearchEngine()
    #     results = engine.search("苹果大改，神似红米")

# 输出结果
