import math
import random
from collections import defaultdict

class SimIDFART:
    """
    SimIDF自适应随机测试算法
    基于文档频率计算真正的TF-IDF,用全局聚合TF-IDF向量近似存档多样性
    """
    
    def __init__(self):
        self.doc_freq = defaultdict(int)      # 文档频率: gram -> 包含该gram的文档数
        self.global_tf_vector = defaultdict(float)  # 全局平均TF: gram -> 平均TF值
        self.total_tests = 0                  # 总测试用例数
        self.archive = []                     # 测试存档
    
    def extract_2grams(self, text):
        """提取2-grams，这里以字符串为例"""
        if len(text) < 2:
            return []
        return [text[i:i+2] for i in range(len(text) - 1)]
    
    def compute_tf(self, grams):
        """计算词频"""
        tf = defaultdict(float)
        total = len(grams)
        if total == 0:
            return tf
        
        for gram in grams:
            tf[gram] += 1.0 / total
        return tf
    
    def update_structures(self, test):
        """更新文档频率和全局TF向量"""
        grams = self.extract_2grams(test)
        unique_grams = set(grams)  # 每个文档中每个gram只计一次
        
        # 更新文档频率
        for gram in unique_grams:
            self.doc_freq[gram] += 1
        
        # 更新全局TF向量（滑动平均）
        local_tf = self.compute_tf(grams)
        for gram, tf_val in local_tf.items():
            current_tf = self.global_tf_vector[gram]
            new_tf = (current_tf * self.total_tests + tf_val) / (self.total_tests + 1)
            self.global_tf_vector[gram] = new_tf
        
        self.total_tests += 1
        self.archive.append(test)
    
    def compute_tfidf_vector(self, test):
        """计算测试用例的TF-IDF向量"""
        grams = self.extract_2grams(test)
        local_tf = self.compute_tf(grams)
        tfidf_vector = {}
        
        for gram, tf_val in local_tf.items():
            df = self.doc_freq.get(gram, 0)
            # 平滑IDF计算，避免除零
            idf = math.log((self.total_tests + 1) / (df + 0.5))
            tfidf_vector[gram] = tf_val * idf
        
        return tfidf_vector
    
    def get_global_tfidf_vector(self):
        """获取全局聚合TF-IDF向量"""
        global_tfidf = {}
        for gram, avg_tf in self.global_tf_vector.items():
            df = self.doc_freq.get(gram, 0)
            idf = math.log((self.total_tests + 1) / (df + 0.5))
            global_tfidf[gram] = avg_tf * idf
        return global_tfidf
    
    def cosine_similarity(self, vec1, vec2):
        """计算两个稀疏向量的余弦相似度"""
        dot_product = 0.0
        norm1 = 0.0
        norm2 = 0.0
        
        # 计算点积和vec1的范数
        for gram, val1 in vec1.items():
            val2 = vec2.get(gram, 0.0)
            dot_product += val1 * val2
            norm1 += val1 * val1
        
        # 计算vec2的范数
        for val2 in vec2.values():
            norm2 += val2 * val2
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (math.sqrt(norm1) * math.sqrt(norm2))
    
    def diversity_score(self, candidate):
        """计算候选测试用例的多样性分数"""
        candidate_vector = self.compute_tfidf_vector(candidate)
        global_vector = self.get_global_tfidf_vector()
        
        similarity = self.cosine_similarity(candidate_vector, global_vector)
        return 1.0 - similarity  # 返回距离，越大越多样
    
    def reset(self):
        """重置算法状态"""
        self.doc_freq.clear()
        self.global_tf_vector.clear()
        self.total_tests = 0
        self.archive = []

# 全局实例，用于测试
simidf_art = SimIDFART()