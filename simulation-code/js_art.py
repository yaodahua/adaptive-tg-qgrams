import math
from collections import defaultdict


# 最大内存对数查找表大小，覆盖计数到10k
# MAX_MEM_LOG = 10_000  # covers counts up to 10k
# 预计算的对数查找表，提高计算性能
# log_lut = [0.0] + [math.log(i) for i in range(1, MAX_MEM_LOG + 1)]

# def log_lookup(c: int) -> float:
#     """快速log计算 c≤MAX_MEM_LOG时查表 否则回退到math.log"""
#     return log_lut[c] if c <= MAX_MEM_LOG else math.log(c)


def compute_js_divergence(global_dict, candidate_dict, global_total=None, candidate_total=None):
    """
    计算候选字典与全局字典的JS散度
    
    优化: 直接在循环中计算,避免中间字典的创建
    减少字典查找和重复计算,提高性能
    
    Args:
        global_dict: 全局2-gram频率字典
        candidate_dict: 候选2-gram频率字典
        global_total: 全局字典总和（可选，避免重复计算）
        candidate_total: 候选字典总和（可选，避免重复计算）
    
    Returns:
        JS散度值
    """
    # 计算总频率（如果未提供参数）
    if global_total is None:
        global_total = sum(global_dict.values())
    if candidate_total is None:
        candidate_total = sum(candidate_dict.values())
    
    # 如果任一字典为空，返回0
    if global_total == 0 or candidate_total == 0:
        return 0.0
    
    # 优化: 避免重复计算倒数
    inv_global_total = 1.0 / global_total
    inv_candidate_total = 1.0 / candidate_total
    
    # 优化: 使用更高效的集合合并策略
    # 优先遍历较小的字典以减少迭代次数
    if len(global_dict) < len(candidate_dict):
        smaller_dict, larger_dict = global_dict, candidate_dict
    else:
        smaller_dict, larger_dict = candidate_dict, global_dict
    
    # 平滑参数
    epsilon = 1e-10
    
    # 计算JS散度
    js_div = 0.0
    
    # 优化: 减少字典查找次数
    # 首先处理较小字典中的gram
    for gram in smaller_dict:
        g_count = global_dict.get(gram, 0)
        c_count = candidate_dict.get(gram, 0)
        
        # 计算概率
        p = g_count * inv_global_total
        q = c_count * inv_candidate_total
        m = (p + q) * 0.5
        
        # 计算KL散度 KL(P||M)
        if p > epsilon and m > epsilon:
            js_div += p * math.log(p / m)
        
        # 计算KL散度 KL(Q||M)
        if q > epsilon and m > epsilon:
            js_div += q * math.log(q / m)
    
    # 然后处理较大字典中独有的gram
    for gram in larger_dict:
        if gram not in smaller_dict:
            g_count = global_dict.get(gram, 0)
            c_count = candidate_dict.get(gram, 0)
            
            # 计算概率
            p = g_count * inv_global_total
            q = c_count * inv_candidate_total
            m = (p + q) * 0.5
            
            # 计算KL散度 KL(P||M)
            if p > epsilon and m > epsilon:
                js_div += p * math.log(p / m)
            
            # 计算KL散度 KL(Q||M)
            if q > epsilon and m > epsilon:
                js_div += q * math.log(q / m)
    
    js_div *= 0.5
    
    return js_div


class IncrementalJS:
    """
    增量JS散度计算类
    维护全局2-gram频率分布，用于与候选测试用例比较
    """
    
    def __init__(self):
        self.global_dict = defaultdict(int)  # 优化: 使用defaultdict避免键检查
        self.total_count = 0   # 总频率计数
    
    def update(self, new_dict):
        """
        更新全局频率字典
        
        优化: 使用defaultdict直接累加，避免键存在性检查
        
        Args:
            new_dict: 新的2-gram频率字典
        """
        # 优化: 直接累加，无需检查键是否存在
        for gram, count in new_dict.items():
            self.global_dict[gram] += count
        
        # 优化: 避免重复计算总和
        self.total_count += sum(new_dict.values())
    
    def compute_js(self, candidate_dict):
        """
        计算候选字典与全局字典的JS散度
        
        优化: 使用预计算的总和，避免重复计算
        
        Args:
            candidate_dict: 候选2-gram频率字典
        
        Returns:
            JS散度值
        """
        # 优化: 使用预计算的全局总和，避免重复计算
        candidate_total = sum(candidate_dict.values())
        return compute_js_divergence(
            self.global_dict, 
            candidate_dict, 
            global_total=self.total_count,  # 使用预计算的全局总和
            candidate_total=candidate_total
        )
    
    def reset(self):
        """
        重置状态
        """
        self.global_dict = {}
        self.total_count = 0
