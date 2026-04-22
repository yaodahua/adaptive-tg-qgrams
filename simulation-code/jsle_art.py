import math
from collections import defaultdict
from enum import Enum


class BoundaryScheme(Enum):
    """边界编码方案枚举"""
    SCHEME_A = "single_side"  
    # 单边独立边界，例子：abc -> _abc -> _, ab, bc

    SCHEME_B = "double_side"  
    # 双边组合边界，例子：abc -> _abc_ -> _a, ab, bc, c_

    SCHEME_C = "hybrid"      
    # 混合边界，例子：abc -> _abc_ -> _, ab, bc, c_

def encode_with_boundary(sequence, scheme=BoundaryScheme.SCHEME_A, q=2):
    """
    这个函数实际实验的时候用
    使用边界标记对序列进行Q-gram编码
    
    Args:
        sequence: 原始序列（字符串或列表）
        scheme: 边界编码方案
        q: Q-gram的大小
    
    Returns:
        编码后的Q-gram频率字典
    """
    if isinstance(sequence, list):
        sequence = ''.join(sequence)

    
    # 第一次遇到全新的 gram（新 key），自动先给这个 key 初始 = 0
    freq_dict = defaultdict(int) 
    # 统计每个二元组出现多少次 → 用 int
    # 记录每个二元组出现在哪些位置 → 用 list
    
    
    if scheme == BoundaryScheme.SCHEME_A:
        extended_s = "_" + sequence
        if len(sequence) >= 1:
            freq_dict['_'] += 1 # 边界标记_单独计数
        
        for i in range(len(sequence) - 1): #i从0开始 
            gram = extended_s[i+1:i+1+q]#跳过边界标记_，从下标 i+1 开始，向右截取 q 个字符
            freq_dict[gram] += 1
    
    elif scheme == BoundaryScheme.SCHEME_B:
        extended_s = "_" + sequence + "_"
        for i in range(len(extended_s) - q + 1):
            gram = extended_s[i:i+q]
            freq_dict[gram] += 1
    
    elif scheme == BoundaryScheme.SCHEME_C:
        extended_s = "_" + sequence + "_"
        
        if len(sequence) >= 1:
            freq_dict['_'] += 1
        
        for i in range(1, len(sequence)):
            gram = sequence[i-1:i+1]
            freq_dict[gram] += 1
        
        if len(sequence) >= 1:
            freq_dict[sequence[-1] + '_'] += 1
    
    return freq_dict

def encode_with_boundary_gramshow(sequence, scheme=BoundaryScheme.SCHEME_A, q=2):
    """
    这个函数做在test中展示用的，返回编码后的Q-gram列表和频率字典
    使用边界标记对序列进行Q-gram编码
    
    Args:
        sequence: 原始序列（字符串或列表）
        scheme: 边界编码方案
        q: Q-gram的大小
    
    Returns:
        编码后的Q-gram列表和频率字典
    """
    if isinstance(sequence, list):
        sequence = ''.join(sequence)
    
    grams = []
    freq_dict = defaultdict(int)
    
    if scheme == BoundaryScheme.SCHEME_A:
        extended_s = "_" + sequence
        if len(sequence) >= 1:
            grams.append('_')
            freq_dict['_'] += 1
        
        for i in range(len(sequence) - 1):
            gram = extended_s[i+1:i+1+q]
            grams.append(gram)
            freq_dict[gram] += 1
    
    elif scheme == BoundaryScheme.SCHEME_B:
        extended_s = "_" + sequence + "_"
        for i in range(len(extended_s) - q + 1):
            gram = extended_s[i:i+q]
            grams.append(gram)
            freq_dict[gram] += 1
    
    elif scheme == BoundaryScheme.SCHEME_C:
        extended_s = "_" + sequence + "_"
        
        if len(sequence) >= 1:
            grams.append('_')
            freq_dict['_'] += 1
        
        for i in range(1, len(sequence)):
            gram = sequence[i-1:i+1]
            grams.append(gram)
            freq_dict[gram] += 1
        
        if len(sequence) >= 1:
            gram = sequence[-1] + '_'
            grams.append(gram)
            freq_dict[gram] += 1
    
    return grams, freq_dict


def compute_js_divergence(global_dict, candidate_dict, global_total=None, candidate_total=None):
    """
    计算候选字典与全局字典的JS散度
    
    Args:
        global_dict: 全局Q-gram频率字典
        candidate_dict: 候选Q-gram频率字典
        global_total: 全局字典总和（可选）
        candidate_total: 候选字典总和（可选）
    
    Returns:
        JS散度值
    """
    if global_total is None:
        global_total = sum(global_dict.values())
    if candidate_total is None:
        candidate_total = sum(candidate_dict.values())
    
    if global_total == 0 or candidate_total == 0:
        return 0.0
    
    inv_global_total = 1.0 / global_total
    inv_candidate_total = 1.0 / candidate_total
    
    # 优化: 优先遍历较小的字典
    if len(global_dict) < len(candidate_dict):
        smaller_dict, larger_dict = global_dict, candidate_dict
    else:
        smaller_dict, larger_dict = candidate_dict, global_dict
    
    epsilon = 1e-10
    js_div = 0.0
    
    # 处理较小字典中的gram
    for gram in smaller_dict:
        g_count = global_dict.get(gram, 0)
        c_count = candidate_dict.get(gram, 0)
        
        p = g_count * inv_global_total
        q = c_count * inv_candidate_total
        m = (p + q) * 0.5
        
        if p > epsilon and m > epsilon:
            js_div += p * math.log(p / m)
        if q > epsilon and m > epsilon:
            js_div += q * math.log(q / m)
    
    # 处理较大字典中独有的gram
    for gram in larger_dict:
        if gram not in smaller_dict:
            g_count = global_dict.get(gram, 0)
            c_count = candidate_dict.get(gram, 0)
            
            p = g_count * inv_global_total
            q = c_count * inv_candidate_total
            m = (p + q) * 0.5
            
            if p > epsilon and m > epsilon:
                js_div += p * math.log(p / m)
            if q > epsilon and m > epsilon:
                js_div += q * math.log(q / m)
    
    js_div *= 0.5
    return js_div


class JSLE_ART:
    """
    JSLE-ART算法实现类
    """
    
    def __init__(self, boundary_scheme=BoundaryScheme.SCHEME_A, q=2):
        self.boundary_scheme = boundary_scheme
        self.q = q
        self.Qcount = defaultdict(int)  # 累积Q-gram计数
        self.total_count = 0  # 累积Q-gram总数（优化性能）
        self.Z = []  # 已执行的测试用例集合
        
    def get_P_Z(self):
        """获取当前执行测试用例的分布P_Z"""
        total = sum(self.Qcount.values())
        if total == 0:
            return {}
        
        P_Z = {}
        for gram, count in self.Qcount.items():
            P_Z[gram] = count / total
        return P_Z
    
    def select_test_case(self, candidate_set):
        """
        从候选集中选择最优测试用例
        
        Args:
            candidate_set: 候选测试用例列表
            
        Returns:
            最优测试用例及其JS分数
        """
        best_score = -1
        best_candidate = None
        
        for candidate in candidate_set:
            # 编码候选测试用例
            freq_dict = encode_with_boundary(candidate, self.boundary_scheme, self.q)
            
            # 计算JS散度（使用预计算的全局总和优化性能）
            candidate_total = sum(freq_dict.values())
            # print(self.total_count,candidate_total)
            js_score = compute_js_divergence(
                self.Qcount, 
                freq_dict, 
                global_total=self.total_count,
                candidate_total=candidate_total
            )
            
            if js_score > best_score:
                best_score = js_score
                best_candidate = candidate
        
        return best_candidate, best_score
    
    def update(self, new_test_case):
        """
        更新算法状态
        
        Args:
            new_test_case: 新执行的测试用例
        """
        # 编码测试用例
        new_dict = encode_with_boundary(new_test_case, self.boundary_scheme, self.q)
        
        # 更新Qcount和total_count
        for gram, count in new_dict.items():
            self.Qcount[gram] += count
        self.total_count += sum(new_dict.values())
        # print(f"总的Q-gram总数: {self.total_count}")
        
        # 添加到已执行集合
        self.Z.append(new_test_case)
    
    def reset(self):
        """重置算法状态"""
        self.Qcount.clear()
        self.total_count = 0
        self.Z.clear()


# 测试函数
def test_jsle_art():
    """测试JSLE-ART算法"""
    # 创建JSLE-ART实例
    jsle_art_a = JSLE_ART(boundary_scheme=BoundaryScheme.SCHEME_A)
    jsle_art_b = JSLE_ART(boundary_scheme=BoundaryScheme.SCHEME_B)
    jsle_art_c = JSLE_ART(boundary_scheme=BoundaryScheme.SCHEME_C)
    
    scheme_list = [jsle_art_a, jsle_art_b, jsle_art_c]
    for scheme in scheme_list:
        jsle_art = scheme
        # jsle_art.reset()
        grams = []
        freq = {}

        print(f"当前边界方案: {jsle_art.boundary_scheme.name}")
        # 初始测试用例
        t0 = "abcabc"
        print(f"初始测试用例: {t0}")
        
        # 编码并显示结果
        grams, freq = encode_with_boundary_gramshow(t0, jsle_art.boundary_scheme)
        print(f"编码后的Q-grams: {grams}")
        print(f"频率分布: {freq}")
        
        # 更新算法状态
        jsle_art.update(t0)
        print(f"初始的Qcount: {dict(jsle_art.Qcount)}")
        
        # 一轮候选集测试
        candidates = ["def", "abc", "xyz"]
        best, score = jsle_art.select_test_case(candidates)
        print(f"候选集: {candidates}")
        print(f"最优候选分数: {score}")
        jsle_art.update(best)
        print(f"一轮选择后的Qcount: {dict(jsle_art.Qcount)}")

        # 二轮候选集测试
        candidates = ["qwer","hjkl", "abccba"]
        best,score = jsle_art.select_test_case(candidates)
        print(f"候选集: {candidates}")
        print(f"最优候选分数: {score}")
        jsle_art.update(best)
        print(f"二轮选择后的Qcount: {dict(jsle_art.Qcount)}")
        #分行
        print("----------------------------------------")


if __name__ == "__main__":
    test_jsle_art()

#元组形式的encode
# def encode_with_boundary_gramshow(sequence, scheme=BoundaryScheme.SCHEME_A, q=2):
#     """
#     使用边界标记对序列进行Q-gram编码
    
#     Args:
#         sequence: 原始序列（字符串或列表）
#         scheme: 边界编码方案
#         q: Q-gram的大小
    
#     Returns:
#         编码后的Q-gram列表和频率字典
#     """
# if isinstance(sequence, str):
#     sequence = list(sequence)

# freq_dict = defaultdict(int)

# if scheme == BoundaryScheme.SCHEME_A:
#     extended_seq = ['START'] + sequence
#     if len(sequence) >= 1:
#         freq_dict[tuple(['START'])] += 1
    
#     for i in range(1, len(extended_seq) - 1):
#         gram = tuple(extended_seq[i:i+q])
#         freq_dict[gram] += 1

# elif scheme == BoundaryScheme.SCHEME_B:
#     extended_seq = ['START'] + sequence + ['END']
#     for i in range(len(extended_seq) - q + 1):
#         gram = tuple(extended_seq[i:i+q])
#         freq_dict[gram] += 1

# elif scheme == BoundaryScheme.SCHEME_C:
#     extended_seq = ['START'] + sequence + ['END']
    
#     if len(sequence) >= 1:
#         freq_dict[tuple(['START'])] += 1
    
#     for i in range(1, len(extended_seq) - 2):
#         gram = tuple(extended_seq[i:i+q])
#         freq_dict[gram] += 1
    
#     if len(sequence) >= 1:
#         freq_dict[tuple([sequence[-1], 'END'])] += 1

# return freq_dict

# def encode_with_boundary(sequence, scheme=BoundaryScheme.SCHEME_A, q=2):
#     """
#     使用边界标记对序列进行Q-gram编码
    
#     Args:
#         sequence: 原始序列（字符串或列表）
#         scheme: 边界编码方案
#         q: Q-gram的大小
    
#     Returns:
#         编码后的Q-gram列表和频率字典
#     """
#     if isinstance(sequence, str):
#         sequence = list(sequence)
    
#     grams = []
    
#     if scheme == BoundaryScheme.SCHEME_A:
#         # Scheme A: 单边独立边界
#         # 编码序列: [START, m1, m2, ..., mL]
#         # 2-grams: [START] + [m1|m2, m2|m3, ..., m_{L-1}|mL]

#         extended_seq = ['START'] + sequence
#         # print(f"原seq长度，现在的seq长度: {len(sequence)}, {len(extended_seq)}")
#         # 处理START作为独立token
#         if len(sequence) >= 1:
#             grams.append(tuple(['START']))
        
#         # 处理中间部分
#         for i in range(1, len(extended_seq) - 1):  # 跳过START
#             gram = tuple(extended_seq[i:i+q])
#             grams.append(gram)
    
#     elif scheme == BoundaryScheme.SCHEME_B:
#         # Scheme B: 双边组合边界
#         # 编码序列: [START, m1, m2, ..., mL, END]
#         # 2-grams: [START|m1] + [m1|m2, m2|m3, ..., m_{L-1}|mL] + [mL|END]
#         extended_seq = ['START'] + sequence + ['END']
#         for i in range(len(extended_seq) - q + 1):
#             gram = tuple(extended_seq[i:i+q])
#             grams.append(gram)
    
#     elif scheme == BoundaryScheme.SCHEME_C:
#         # Scheme C: 混合边界
#         # 编码序列: [START, m1, m2, ..., mL, END]
#         # 2-grams: [START] + [m1|m2, m2|m3, ..., m_{L-1}|mL] + [mL|END]
#         extended_seq = ['START'] + sequence + ['END']
        
#         # 处理START作为独立token
#         if len(sequence) >= 1:
#             grams.append(tuple(['START']))
        
#         # 处理中间部分
#         for i in range(1, len(extended_seq) - 2):  # 跳过START和END
#             gram = tuple(extended_seq[i:i+q])
#             grams.append(gram)
        
#         # 处理END组合边界
#         if len(sequence) >= 1:
#             grams.append(tuple([sequence[-1], 'END']))
    
#     # 计算频率分布
#     freq_dict = defaultdict(int)
#     for gram in grams:
#         freq_dict[gram] += 1
    
#     return grams, freq_dict