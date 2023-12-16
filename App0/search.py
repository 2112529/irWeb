class NewsSearchEngine:
    def __init__(self):
        self.documents = self.load_documents()
        self.inverted_index = self.build_inverted_index(self.documents)
        self.document_vectors = self.build_document_vectors(self.documents)


    def load_documents(self):
        # 从 news_article 表中加载文档数据
        documents = NewsArticle.objects.all()
        document_data = []
        for doc in documents:
            # 这里您可以根据需要选择要加载的字段
            document_data.append({
                'id': doc.id,
                'title': doc.title,
                'keywords': doc.keywords,
                'description': doc.description
            })
        return document_data

    def build_inverted_index(self, documents):
        inverted_index = {}
        for doc in documents:
            doc_id = doc['id']
            content = doc['title'] + ' ' + doc['keywords'] + ' ' + doc['description']
            # 使用 jieba 进行中文分词
            words = set(jieba.cut(content))
            for word in words:
                if word not in inverted_index:
                    inverted_index[word] = [doc_id]
                else:
                    inverted_index[word].append(doc_id)
        return inverted_index

    def build_document_vectors(self, documents):
        # Step 1: 计算 TF 和 文档中的词总数
        tf = defaultdict(dict)
        doc_word_count = defaultdict(int)
        for doc in documents:
            doc_id = doc['id']
            content = doc['title'] + ' ' + doc['keywords'] + ' ' + doc['description']
            words = jieba.lcut(content)
            for word in words:
                tf[doc_id][word] = tf[doc_id].get(word, 0) + 1
                doc_word_count[doc_id] += 1

        # Step 2: 计算 IDF
        idf = {}
        total_documents = len(documents)
        for doc in tf.values():
            for word in doc:
                idf[word] = idf.get(word, 0) + 1
        for word, count in idf.items():
            idf[word] = math.log(total_documents / count)

        # Step 3: 构建 TF-IDF 向量
        tfidf_vectors = {}
        for doc_id, word_freqs in tf.items():
            tfidf = {}
            for word, freq in word_freqs.items():
                tf_word = freq / doc_word_count[doc_id]
                tfidf[word] = tf_word * idf[word]
            tfidf_vectors[doc_id] = tfidf

        return tfidf_vectors

    def process_query(self, query):
        # 分词
        query_words = list(jieba.cut(query))
        # 计算 TF
        tf_query = {}
        for word in query_words:
            tf_query[word] = tf_query.get(word, 0) + 1

        # 将查询转换为向量（使用已计算的 IDF 值）
        query_vector = {}
        for word, freq in tf_query.items():
            if word in self.idf:  # 只考虑在文档集中出现过的词
                query_vector[word] = freq * self.idf[word]

        return query_vector

    def search(self, query):
        query_vector = self.process_query(query)
        results = []
        for doc_id, doc_vector in self.document_vectors.items():
            similarity = self.calculate_similarity(query_vector, doc_vector)
            results.append((doc_id, similarity))
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
            # 避免除以零
            return 0

        # 计算余弦相似度
        cosine_similarity = dot_product / (magnitude1 * magnitude2)
        return cosine_similarity

# 使用
# engine = NewsSearchEngine()
# results = engine.search("苹果大改，神似红米")
# 输出结果
