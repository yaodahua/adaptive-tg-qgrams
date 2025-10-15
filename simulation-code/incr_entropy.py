import math


# 最大内存对数查找表大小，覆盖计数到10k
MAX_MEM_LOG = 10_000  # covers counts up to 10k
# 预计算的对数查找表，提高计算性能
log2_lut = [0.0] + [math.log2(i) for i in range(1, MAX_MEM_LOG + 1)]

def log2lookup(c: int) -> float:
    """快速log₂计算 c≤MAX_C时查表 否则回退到math.log2"""
    return log2_lut[c] if c <= MAX_MEM_LOG else math.log2(c)

def log2(p):
    """计算以2为底的对数 处理p=0的情况"""
    return math.log(p, 2) if p > 0 else 0

# 使用查找表优化的增量信息熵计算类
class IncrementalEntropy:
    def __init__(self):
        self.log_count_ = 0.0  # 对数计数总和
        self.tot_count_ = 0.0  # 总计数
        self.dict_ = None      # 存储频率字典

    def standard_entropy(self, dict):
        """标准信息熵计算"""
        s = sum(dict.values())
        return sum([-(r/s) * log2(r/s) for r in dict.values()])

    def alt_entropy(self, dict):
        """替代熵计算方法，使用查找表优化"""
        self.dict_ = dict.copy()
        self.log_count_ = sum([r * log2lookup(r) for r in dict.values()])
        self.tot_count_ = sum([r for r in dict.values()])
        return -self.log_count_ / self.tot_count_ + log2lookup(self.tot_count_)

    def store_changes(self, changes):
        """存储变化并更新内部状态"""
        self.tot_count_ += sum([r for r in changes.values()])
        for k in changes:
            prev_val = 0 if not k in self.dict_ else self.dict_[k]
            self.log_count_ += (prev_val + changes[k]) * log2lookup(prev_val + changes[k]) - prev_val * log2lookup(prev_val)
            self.dict_[k] = prev_val + changes[k]

    def inc_entropy(self, changes):
        """增量计算信息熵，不修改内部状态"""
        if self.dict_ is None:
            return self.alt_entropy(changes)
        tot_count_delta = sum([r for r in changes.values()])
        log_count_delta = 0.0
        for k in changes:
            prev_val = 0 if not k in self.dict_ else self.dict_[k]
            log_count_delta += (prev_val + changes[k]) * log2lookup(prev_val + changes[k]) - prev_val * log2lookup(prev_val)
        tmp_tot_count_ = self.tot_count_ + tot_count_delta
        tmp_log_count_ = self.log_count_ + log_count_delta
        return -tmp_log_count_ / tmp_tot_count_ + log2lookup(tmp_tot_count_)


# 使用浮点运算的增量信息熵计算类（精度更高）
class IncrementalEntropyFloat:
    def __init__(self):
        self.log_count_ = 0.0  # 对数计数总和
        self.tot_count_ = 0.0  # 总计数
        self.dict_ = None      # 存储频率字典

    def standard_entropy(self, dict):
        """标准信息熵计算"""
        s = sum(dict.values())
        return sum([-(r/s) * log2(r/s) for r in dict.values()])

    def alt_entropy(self, dict):
        """替代熵计算方法，使用浮点运算"""
        self.dict_ = dict.copy()
        self.log_count_ = sum([r * log2(r) for r in dict.values()])
        self.tot_count_ = sum([r for r in dict.values()])
        return -self.log_count_ / self.tot_count_ + log2(self.tot_count_)

    def store_changes(self, changes):
        """存储变化并更新内部状态"""
        self.tot_count_ += sum([r for r in changes.values()])
        for k in changes:
            prev_val = 0 if not k in self.dict_ else self.dict_[k]
            self.log_count_ += (prev_val + changes[k]) * log2(prev_val + changes[k]) - prev_val * log2(prev_val)
            self.dict_[k] = prev_val + changes[k]

    def inc_entropy(self, changes):
        """增量计算信息熵，不修改内部状态"""
        if self.dict_ is None:
            return self.alt_entropy(changes)
        tot_count_delta = sum([r for r in changes.values()])
        log_count_delta = 0.0
        for k in changes:
            prev_val = 0 if not k in self.dict_ else self.dict_[k]
            log_count_delta += (prev_val + changes[k]) * log2(prev_val + changes[k]) - prev_val * log2(prev_val)
        tmp_tot_count_ = self.tot_count_ + tot_count_delta
        tmp_log_count_ = self.log_count_ + log_count_delta
        return -tmp_log_count_ / tmp_tot_count_ + log2(tmp_tot_count_)

