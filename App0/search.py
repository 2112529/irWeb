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
from App0.models import Postings1,NewsArticle1


class NewsSearchEngine:
    def __init__(self):
        self.stop_words_path = "stop_words.txt"
        self.stop_words_encoding = "utf-8"
        self.idf_path = "idf.txt"
        self.terms={}
        self.dt_matrix = None
        self.doc_dir_path = "News1/"
        self.inverted_index = {}

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
        #  self.terms = {}
        dt = []
        for file in files:
            # root = ET.parse(self.doc_dir_path + file).getroot()
            # title = root.find('title').text
            # # discription=root.find('description').text
            # keywords=root.find('keywords').text
            # if title==None : 
            #     title = ' '
            # # if discription==None : 
            # #     discription = ' '
            # if keywords==None :
            #     keywords = ' '
            # docid = int(root.find('id').text)
            docid=file.news_id
            title = file.title
            if title==None : 
                title = ' '
            keywords = file.keywords
            tags = jieba.analyse.extract_tags(title + '。' + keywords, topK=topK, withWeight=True)
            #tags = jieba.analyse.extract_tags(title, topK=topK, withWeight=True)
            cleaned_dict = {}
            for word, tfidf in tags:
                word = word.strip().lower()
                if word == '' or self.is_number(word):
                    continue
                cleaned_dict[word] = tfidf
                if word not in self.terms:
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

        # dt_matrix = pd.DataFrame(dt_matrix)
        
        self.dt_matrix = pd.DataFrame(dt_matrix)
        self.dt_matrix.index = self.dt_matrix[0]
        # print('dt_matrix shape:(%d %d)'%(self.dt_matrix.shape))
        # return dt_matrix


    def process_query(self, query):
        # 分词
        # jieba.analyse.set_stop_words(self.stop_words_path)
        # query_words=jieba.analyse.extract_tags(query, topK=100, withWeight=False)
        query_words = list(jieba.cut(query))
        print(query_words)
        # print(self.terms)
        
        # 计算 TF
        tf_query = {}
        for word in query_words:
            print(word)
            word = word.strip().lower()
            if word in self.terms and word != '' and not self.is_number(word):
                if word not in tf_query:
                    tf_query[word] = 1
                else:
                    tf_query[word] += 1
                # tf_query[word] = tf_query.get(word,0) + 1
        print(tf_query)
        # 将查询转换为向量
        query_vector = [0] * len( self.terms)
        for word, freq in tf_query.items():
            index =  self.terms.get(word)
            if index is not None:
                query_vector[index] = freq
        # print(query_vector)
        return query_vector

    def search(self, query):
       
        # print(query_vector)
        
        # files = listdir(self.doc_dir_path)
        files=NewsArticle1.objects.all()
        self.construct_dt_matrix(files)
        # print(self.terms)
        # print(len(self.terms))
        query_vector = self.process_query(query)
        # print(query_vector)
        # # print(self.dt_matrix)
        results = []
        for i, row in self.dt_matrix.iterrows():
            doc_vector = row[1:]  # 跳过文档ID
            similarity = self.calculate_similarity(query_vector, doc_vector)
            results.append((row[0], similarity))  # row[0] 是文档ID
        results.sort(key=lambda x: x[1], reverse=True)  # 按相似度排序

        # 截取相似度排名前五的文档ID
        # 如果前五个文档中有的相似度低于第一个文档的一半，则删除
        if results:
            highest_similarity = results[0][1]  # 最高相似度
            top_five_document_ids = [doc_id for doc_id, similarity in results[:5] if similarity >= highest_similarity / 2]
        else:
            top_five_document_ids = []
        # 打印每个文档ID对应的向量
        for doc_id in top_five_document_ids:
            doc_vector = self.dt_matrix.loc[doc_id][1:]  # 跳过文档ID，获取向量
            print(f"Document ID: {doc_id}, Vector: {doc_vector.tolist()}")
        return top_five_document_ids



    def calculate_similarity(self, vec1, vec2):
        # 计算两个向量的点积
        dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))

        # 计算两个向量的模
        magnitude1 = math.sqrt(sum(x**2 for x in vec1))
        magnitude2 = math.sqrt(sum(x**2 for x in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0

        # 计算余弦相似度
        cosine_similarity = dot_product / (magnitude1 * magnitude2)
        return cosine_similarity



    # 接下来的内容是用于通配查询
    
    def load_inverted_index(self):
        postings = Postings1.objects.all()
        for posting in postings:
            # 分割每一行，并进一步分割每一行中的数据
            docs = posting.docs.strip().split('\n')  # 先按行分割
            doc_list = []
            for doc in docs:
                parts = doc.strip().split('\t')
                if parts and parts[0].isdigit():  # 确保有内容且第一部分是数字
                    doc_id = int(parts[0])  # 将第一个部分转换为整数
                    doc_list.append(doc_id)  # 将doc_id添加到列表中
                # 如果需要，您还可以提取其他信息，如term出现次数和文档词项总数
            self.inverted_index[posting.term] = doc_list



    def process_wild_query(self, query):
        self.load_inverted_index()  # 加载倒排索引
        all_possible_queries = []
        if '*' in query:
            prefix, suffix = query.split('*', 1)
            for term in self.inverted_index.keys():
                if term.startswith(prefix) and term.endswith(suffix):
                    all_possible_queries.append(term)
        elif '?' in query:
            prefix, suffix = query.split('?', 1)
            for term in self.inverted_index.keys():
                if term.startswith(prefix) and term.endswith(suffix) and len(term) == len(query):
                    all_possible_queries.append(term)
        return all_possible_queries



    def search_with_wildcard(self,query):
        expanded_queries = self.process_wild_query(query)
        print(expanded_queries)
        if not expanded_queries or expanded_queries == [['']]:
            return []  # 返回空列表或适当的错误消息
        results = set()  # 使用集合来避免重复的文档ID
        for eq in expanded_queries:
            # 使用扩展后的查询词在倒排索引中搜索匹配的文档
            if eq in self.inverted_index.keys():
                matched_documents_id = self.inverted_index[eq]
                results.update(matched_documents_id)
        print(results)
        return list(results)  # 将结果转换为列表



