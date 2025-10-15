import math
from collections import defaultdict


class TFIDF2Grams:
    """TF-IDF 2-grams计算类"""
    
    def __init__(self):
        self.bigram_freq = defaultdict(int)  # 二元组频率统计
        self.doc_count = 0                  # 文档总数
        self.bigram_doc_count = defaultdict(int)  # 包含每个二元组的文档数
        
    def add_document(self, s: str):
        """添加文档并更新统计信息"""
        self.doc_count += 1
        bigrams = self._extract_bigrams(s)
        
        # 更新二元组频率
        for bigram in bigrams:
            self.bigram_freq[bigram] += 1
        
        # 更新文档频率（每个二元组只计一次）
        unique_bigrams = set(bigrams)
        for bigram in unique_bigrams:
            self.bigram_doc_count[bigram] += 1
    
    def _extract_bigrams(self, s: str):
        """提取字符串的二元组（不考虑边界）"""
        bigrams = []
        for i in range(len(s) - 1):
            bigrams.append(s[i:i+2])
        return bigrams
    
    def tf_idf_score(self, s: str):
        """计算字符串的TF-IDF得分"""
        if self.doc_count == 0:
            return 0.0
        
        bigrams = self._extract_bigrams(s)
        if not bigrams:
            return 0.0
        
        # 计算TF（词频）
        tf_scores = {}
        for bigram in set(bigrams):
            tf = bigrams.count(bigram) / len(bigrams)
            tf_scores[bigram] = tf
        
        # 计算IDF（逆文档频率）
        idf_scores = {}
        for bigram in tf_scores:
            if bigram in self.bigram_doc_count and self.bigram_doc_count[bigram] > 0:
                idf = math.log(self.doc_count / self.bigram_doc_count[bigram])
            else:
                idf = math.log(self.doc_count)  # 新二元组，给予较高权重
            idf_scores[bigram] = idf
        
        # 计算TF-IDF总分
        total_score = 0.0
        for bigram in tf_scores:
            total_score += tf_scores[bigram] * idf_scores[bigram]
        
        return total_score
    
    def novelty_score(self, s: str):
        """计算字符串的新颖性得分 基于TF-IDF"""
        return self.tf_idf_score(s)
    
    def store_changes(self, s: str):
        """存储变化并更新内部状态"""
        self.add_document(s)


class IncrementalTFIDF2Grams:
    """增量TF-IDF 2-grams计算类"""
    
    def __init__(self):
        self.tfidf = TFIDF2Grams()
        
    def inc_tfidf(self, s: str):
        """增量计算TF-IDF得分 不修改内部状态"""
        return self.tfidf.tf_idf_score(s)
    
    def store_changes(self, s: str):
        """存储变化并更新内部状态"""
        self.tfidf.add_document(s)


def bigram_count(dict, s):
    """计算字符串的二元组频率（不考虑边界）"""
    for i in range(len(s) - 1):
        if s[i : i + 2] in dict:
            dict[s[i : i + 2]] += 1
        else:
            dict[s[i : i + 2]] = 1