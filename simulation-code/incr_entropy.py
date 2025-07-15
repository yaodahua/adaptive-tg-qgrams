import math

def log2(p):
    return math.log(p, 2) if p > 0 else 0

class IncrementalEntropy:
    def __init__(self):
        self.log_count_ = 0.0
        self.tot_count_ = 0.0
        self.dict_ = None

    def standard_entropy(self, dict):
        s = sum(dict.values())
        return sum([-(r/s) * log2(r/s) for r in dict.values()])

    def alt_entropy(self, dict):
        self.dict_ = dict.copy()
        self.log_count_ = sum([r * log2(r) for r in dict.values()])
        self.tot_count_ = sum([r for r in dict.values()])
        return -self.log_count_ / self.tot_count_ + log2(self.tot_count_)

    def store_changes(self, changes):
        self.tot_count_ += sum([r for r in changes.values()])
        for k in changes:
            prev_val = 0.0 if not k in self.dict_ else self.dict_[k]
            self.log_count_ += (prev_val + changes[k]) * log2(prev_val + changes[k]) - prev_val * log2(prev_val)
            self.dict_[k] = prev_val + changes[k]

    def inc_entropy(self, changes):
        if self.dict_ is None:
            return self.alt_entropy(changes)
        tot_count_delta = sum([r for r in changes.values()])
        log_count_delta = 0.0
        for k in changes:
            prev_val = 0.0 if not k in self.dict_ else self.dict_[k]
            log_count_delta += (prev_val + changes[k]) * log2(prev_val + changes[k]) - prev_val * log2(prev_val)
        tmp_tot_count_ = self.tot_count_ + tot_count_delta
        tmp_log_count_ = self.log_count_ + log_count_delta
        return -tmp_log_count_ / tmp_tot_count_ + log2(tmp_tot_count_)

