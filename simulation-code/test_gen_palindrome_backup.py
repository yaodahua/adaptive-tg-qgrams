import random
import is_palindrome
import time
import numpy as np
from difflib import SequenceMatcher
import utils
import argparse
import os
import incr_entropy
import tfidf_2grams


def random_string(max_len=100, start_char=97, end_char=122):
    length = random.randint(0, max_len)
    s = ""
    for _ in range(length):
        s += chr(random.randint(start_char, end_char))
    return s

# 中文注释：随机生成字符串
def random_gen(test_gen_budget=100000, stop_at_failure=False, delay=False, max_len=100):
    if stop_at_failure:
        start = time.time()
    f = 0.0
    n = 0
    while n < test_gen_budget or stop_at_failure:
        s = random_string(max_len)
        n += 1
        if is_palindrome.is_palindrom(s, delay) != is_palindrome.is_palindrom_mu1(s):
            f += 1.0
            if stop_at_failure:
                return (n, time.time() - start)
    return f / test_gen_budget

# 中文注释：基于距离的自适应随机测试
def ART_dist(
    test_gen_budget=100,
    W_sample_size=10,
    stop_at_failure=False,
    delay=False,
    max_len=100,
):
    if stop_at_failure:
        start = time.time()
    Z = []
    s = random_string(max_len)
    Z.append(s)
    n = 1
    f = 0.0
    if is_palindrome.is_palindrom(s, delay) != is_palindrome.is_palindrom_mu1(s):
        f += 1.0
        if stop_at_failure:
            return (n, time.time() - start)
    while n < test_gen_budget or stop_at_failure:
        W = []
        W_dist = []
        for i in range(W_sample_size):
            s = random_string(max_len)
            min_dist = np.min([1 - SequenceMatcher(None, a=s, b=z).ratio() for z in Z])
            W.append(s)
            W_dist.append(min_dist)
        s_exec = W[np.argmax(W_dist)]
        n += 1
        if is_palindrome.is_palindrom(s_exec, delay) != is_palindrome.is_palindrom_mu1(
            s_exec
        ):
            f += 1.0
            if stop_at_failure:
                return (n, time.time() - start)
        Z.append(s_exec)
    return f / test_gen_budget

# 中文注释：计算字符串的二元组频率
def bigram_count(dict, s):
    s = "_" + s + "_"
    for i in range(len(s) - 1):
        if s[i : i + 2] in dict:
            dict[s[i : i + 2]] += 1
        else:
            dict[s[i : i + 2]] = 1

# 中文注释：基于二元组频率的自适应随机测试
def ART_bigram(
    test_gen_budget=100,
    W_sample_size=10,
    stop_at_failure=False,
    delay=False,
    max_len=100,
):
    if stop_at_failure:
        start = time.time()
    Z = []
    bigram_dict = {}
    s = random_string(max_len)
    Z.append(s)
    bigram_count(bigram_dict, s)
    ient = incr_entropy.IncrementalEntropy()
    ient.inc_entropy(bigram_dict)
    n = 1
    f = 0.0
    if is_palindrome.is_palindrom(s, delay) != is_palindrome.is_palindrom_mu1(s):
        f += 1.0
        if stop_at_failure:
            return (n, time.time() - start)
    while n < test_gen_budget or stop_at_failure:
        W = []
        W_ent = []
        for i in range(W_sample_size):
            s = random_string(max_len)
            local_bigram_dict = {}  # = dict(bigram_dict)
            bigram_count(local_bigram_dict, s)
            ent = ient.inc_entropy(local_bigram_dict)
            W.append(s)
            W_ent.append(ent)
        s_exec = W[np.argmax(W_ent)]
        n += 1
        if is_palindrome.is_palindrom(s_exec, delay) != is_palindrome.is_palindrom_mu1(
            s_exec
        ):
            f += 1.0
            if stop_at_failure:
                return (n, time.time() - start)
        Z.append(s_exec)
        # bigram_count(bigram_dict, s_exec)
        local_bigram_dict = {}
        bigram_count(local_bigram_dict, s_exec)
        ient.store_changes(local_bigram_dict)
    return f / test_gen_budget


# 中文注释：基于TF-IDF 2-grams的自适应随机测试
def ART_tfidf(
    test_gen_budget=100,
    W_sample_size=10,
    stop_at_failure=False,
    delay=False,
    max_len=100,
):
    """使用TF-IDF 2-grams替代信息熵的自适应随机测试"""
    if stop_at_failure:
        start = time.time()
    Z = []
    s = random_string(max_len)
    Z.append(s)
    
    # 使用TF-IDF替代信息熵
    itfidf = tfidf_2grams.IncrementalTFIDF2Grams()
    itfidf.store_changes(s)  # 添加第一个文档
    
    n = 1
    f = 0.0
    if is_palindrome.is_palindrom(s, delay) != is_palindrome.is_palindrom_mu1(s):
        f += 1.0
        if stop_at_failure:
            return (n, time.time() - start)
    
    while n < test_gen_budget or stop_at_failure:
        W = []
        W_tfidf = []
        for i in range(W_sample_size):
            s = random_string(max_len)
            tfidf_score = itfidf.inc_tfidf(s)  # 计算TF-IDF得分
            W.append(s)
            W_tfidf.append(tfidf_score)
        
        # 选择TF-IDF得分最高的候选（新颖性最高）
        s_exec = W[np.argmax(W_tfidf)]
        n += 1
        
        if is_palindrome.is_palindrom(s_exec, delay) != is_palindrome.is_palindrom_mu1(s_exec):
            f += 1.0
            if stop_at_failure:
                return (n, time.time() - start)
        
        Z.append(s_exec)
        itfidf.store_changes(s_exec)  # 更新TF-IDF统计
    
    return f / test_gen_budget

# 中文注释：计算f-measure和t-measure
def f_t_measure(
    runs_rand=1000, runs_dist=10, runs_bigrams=100, runs_tfidf=100, delay=False, max_len=100
):
    res_rand = []
    print(f'**** Running Rand ({runs_rand}) ****')
    for i in range(runs_rand):
        res_rand.append(random_gen(stop_at_failure=True, delay=delay, max_len=max_len))
        print(f"{i+1}/{runs_rand}")
    # res_rand = [random_gen(stop_at_failure=True) for i in range(runs_rand)]
    res_dist = []
    print(f'**** Running Dist ({runs_dist}) ****')
    for i in range(runs_dist):
        res_dist.append(ART_dist(stop_at_failure=True, delay=delay, max_len=max_len))
        print(f"{i+1}/{runs_dist}")
    # res_dist = [ART_dist(stop_at_failure=True) for i in range(runs_dist)]
    res_bigrams = []
    print(f'**** Running Bigram ({runs_bigrams}) ****')
    for i in range(runs_bigrams):
        res_bigrams.append(
            ART_bigram(stop_at_failure=True, delay=delay, max_len=max_len)
        )
        print(f"{i+1}/{runs_bigrams}")
    # res_bigrams = [ART_bigram(stop_at_failure=True) for i in range(runs_bigrams)]
    res_tfidf = []
    print(f'**** Running TF-IDF ({runs_tfidf}) ****')
    for i in range(runs_tfidf):
        res_tfidf.append(
            ART_tfidf(stop_at_failure=True, delay=delay, max_len=max_len)
        )
        print(f"{i+1}/{runs_tfidf}")
    # res_tfidf = [ART_tfidf(stop_at_failure=True) for i in range(runs_tfidf)]
    f_rand = 0 if runs_rand == 0 else np.mean([n for n, t in res_rand])
    f_dist = 0 if runs_dist == 0 else np.mean([n for n, t in res_dist])
    f_bigrams = 0 if runs_bigrams == 0 else np.mean([n for n, t in res_bigrams])
    f_tfidf = 0 if runs_tfidf == 0 else np.mean([n for n, t in res_tfidf])
    t_rand = 0 if runs_rand == 0 else np.mean([t for n, t in res_rand])
    t_dist = 0 if runs_dist == 0 else np.mean([t for n, t in res_dist])
    t_bigrams = 0 if runs_bigrams == 0 else np.mean([t for n, t in res_bigrams])
    t_tfidf = 0 if runs_tfidf == 0 else np.mean([t for n, t in res_tfidf])
    if runs_rand != 0:
        utils.write_f_t_results(res_rand, "rand", max_len, delay)
    if runs_dist != 0:
        utils.write_f_t_results(res_dist, "dist", max_len, delay)
    if runs_bigrams != 0:
        utils.write_f_t_results(res_bigrams, "bigrams", max_len, delay)
    if runs_tfidf != 0:
        utils.write_f_t_results(res_tfidf, "tfidf", max_len, delay)
    
    # 添加TF-IDF vs Bigram性能对比输出
    if runs_tfidf > 0 and runs_bigrams > 0:
        print("=== TF-IDF vs Bigram 性能对比 ===")
        print(f"F-measure对比: TF-IDF={f_tfidf:.6f} vs Bigram={f_bigrams:.6f}")
        print(f"T-measure对比: TF-IDF={t_tfidf:.6f} vs Bigram={t_bigrams:.6f}")
        print(f"F-measure差异: {f_tfidf - f_bigrams:.6f}")
        print(f"T-measure差异: {t_tfidf - t_bigrams:.6f}")
        
        # 计算性能提升百分比
        if f_bigrams > 0:
            f_improvement = (f_tfidf - f_bigrams) / f_bigrams * 100
            print(f"F-measure提升: {f_improvement:.2f}%")
        
        if t_bigrams > 0:
            t_improvement = (t_tfidf - t_bigrams) / t_bigrams * 100
            print(f"T-measure提升: {t_improvement:.2f}%")
        print()
    
    return ((f_rand, f_dist, f_bigrams, f_tfidf), (t_rand, t_dist, t_bigrams, t_tfidf))

# 中文注释：计算p-measure
def p_measure(
    runs_rand=1000,
    runs_dist=10,
    runs_bigrams=100,
    runs_tfidf=100,
    tgen_budget=50,
    delay=False,
    max_len=100,
):
    res_rand = []
    print(f'**** Running Rand ({runs_rand}) ****')
    for i in range(runs_rand):
        res_rand.append(random_gen(test_gen_budget=tgen_budget, max_len=max_len))
        print(f"{i+1}/{runs_rand}")
    # res_rand = [random_gen(test_gen_budget=tgen_budget) for i in range(runs_rand)]
    res_dist = []
    print(f'**** Running Dist ({runs_dist}) ****')
    for i in range(runs_dist):
        res_dist.append(ART_dist(test_gen_budget=tgen_budget, max_len=max_len))
        print(f"{i+1}/{runs_dist}")
    # res_dist = [ART_dist(test_gen_budget=tgen_budget) for i in range(runs_dist)]
    res_bigrams = []
    print(f'**** Running Bigram ({runs_bigrams}) ****')
    for i in range(runs_bigrams):
        res_bigrams.append(ART_bigram(test_gen_budget=tgen_budget, max_len=max_len))
        print(f"{i+1}/{runs_bigrams}")
    # res_bigrams = [ART_bigram(test_gen_budget=tgen_budget) for i in range(runs_bigrams)]
    res_tfidf = []
    print(f'**** Running TF-IDF ({runs_tfidf}) ****')
    for i in range(runs_tfidf):
        res_tfidf.append(ART_tfidf(test_gen_budget=tgen_budget, max_len=max_len))
        print(f"{i+1}/{runs_tfidf}")
    # res_tfidf = [ART_tfidf(test_gen_budget=tgen_budget) for i in range(runs_tfidf)]
    p_rand = 0 if runs_rand == 0 else np.mean(res_rand)
    p_dist = 0 if runs_dist == 0 else np.mean(res_dist)
    p_bigrams = 0 if runs_bigrams == 0 else np.mean(res_bigrams)
    p_tfidf = 0 if runs_tfidf == 0 else np.mean(res_tfidf)
    if runs_rand != 0:
        utils.write_p_results(res_rand, "rand", max_len, delay)
    if runs_dist != 0:
        utils.write_p_results(res_dist, "dist", max_len, delay)
    if runs_bigrams != 0:
        utils.write_p_results(res_bigrams, "bigrams", max_len, delay)
    if runs_tfidf != 0:
        utils.write_p_results(res_tfidf, "tfidf", max_len, delay)
    
    # 添加TF-IDF vs Bigram P-measure对比输出
    if runs_tfidf > 0 and runs_bigrams > 0:
        print("=== TF-IDF vs Bigram P-measure对比 ===")
        print(f"P-measure对比: TF-IDF={p_tfidf:.6f} vs Bigram={p_bigrams:.6f}")
        print(f"P-measure差异: {p_tfidf - p_bigrams:.6f}")
        
        # 计算性能提升百分比
        if p_bigrams > 0:
            p_improvement = (p_tfidf - p_bigrams) / p_bigrams * 100
            print(f"P-measure提升: {p_improvement:.2f}%")
        print()
    
    return (p_rand, p_dist, p_bigrams, p_tfidf)

# 中文注释：设置命令行参数解析
args = argparse.ArgumentParser()
args.add_argument(
    "--delay",
    help="Add 10 ms delay to the execution of the palindrome function",
    action="store_true",
    default=False,
)
args.add_argument(
    "--max-string-length",
    help="Maximum length of the string input, controlling the failure rate",
    type=int,
    choices=[100, 1000, 10000, 66225],
    default=100,
)
args.add_argument(
    "--runs-rand",
    help="Number of runs for random generation",
    type=int,
    default=1000,
)
args.add_argument(
    "--runs-dist",
    help="Number of runs for ART_dist",
    type=int,
    default=10,
)
args.add_argument(
    "--runs-bigrams",
    help="Number of runs for ART_bigrams",
    type=int,
    default=100,
)
args.add_argument(
    "--runs-tfidf",
    help="Number of runs for ART_tfidf (TF-IDF 2-grams)",
    type=int,
    default=100,
)
#args, _ = args.parse_args()
args = args.parse_args() 

# python test_gen_palindrome.py --max-string-length 100 --runs-rand 100 --runs-dist 100 --runs-bigrams 100 --runs-tfidf 100

if __name__ == "__main__":
    # 66225 ensures failure rate = 1.51e-5 for random generation
    MAX_STR_LENGTH = args.max_string_length
    ADD_DELAY = args.delay
    runs_rand = args.runs_rand
    runs_dist = args.runs_dist
    runs_bigrams = args.runs_bigrams
    runs_tfidf = args.runs_tfidf
    if not os.path.exists('results'):
        os.makedirs('results')
    #确保运行次数为非负整数
    assert runs_rand >= 0, "Number of runs for random generation must be non-negative"
    assert runs_dist >= 0, "Number of runs for ART_dist must be non-negative"
    assert runs_bigrams >= 0, "Number of runs for ART_bigrams must be non-negative"
    assert runs_tfidf >= 0, "Number of runs for ART_tfidf must be non-negative"
    
    #中文注释：根据是否添加延迟，设置文件名后缀
    if ADD_DELAY:
        DELAY_SUFFIX = "_del"  # '_del' when delay is true; '' otherwise
    
    #中文注释：显示当前计算项目
    print("===== Computing p-measure =====")
    p_measure(
        runs_rand=runs_rand,
        runs_dist=runs_dist,
        runs_bigrams=runs_bigrams,
        runs_tfidf=runs_tfidf,
        max_len=MAX_STR_LENGTH,
    )
    print("===== Computing f-measure and t-measure =====")
    f_t_measure(
        runs_rand=runs_rand,
        runs_dist=runs_dist,
        runs_bigrams=runs_bigrams,
        runs_tfidf=runs_tfidf,
        delay=ADD_DELAY,
        max_len=MAX_STR_LENGTH,
    )

    #中文注释：写入统计结果并进行比较
    utils.write_summary_statistics(delay=ADD_DELAY)
    p_val = utils.compare_P_meas(
        f"results/P_measure_bigrams_{MAX_STR_LENGTH}.csv",
        f"results/P_measure_rand_{MAX_STR_LENGTH}.csv",
    )
    p_val1, p_val2 = utils.compare_F_T_meas(
        f"results/F_T_measure_bigrams_{MAX_STR_LENGTH}.csv",
        f"results/F_T_measure_rand_{MAX_STR_LENGTH}.csv",
    )
    #中文注释：打印比较结果
    # print(f'Bigrams vs Rand (P-meas): p-val = {p_val}')
    # print(f'Bigrams vs Rand (F-meas): p-val = {p_val1}')
    # print(f'Bigrams vs Rand (T-meas): p-val = {p_val2}')
    
    # 添加TF-IDF vs Bigram统计显著性检验
    if runs_tfidf > 0 and runs_bigrams > 0:
        print("===== TF-IDF vs Bigram 统计显著性检验 =====")
        p_val_tfidf_bigram = utils.compare_P_meas(
            f"results/P_measure_tfidf_{MAX_STR_LENGTH}.csv",
            f"results/P_measure_bigrams_{MAX_STR_LENGTH}.csv",
        )
        p_val1_tfidf_bigram, p_val2_tfidf_bigram = utils.compare_F_T_meas(
            f"results/F_T_measure_tfidf_{MAX_STR_LENGTH}.csv",
            f"results/F_T_measure_bigrams_{MAX_STR_LENGTH}.csv",
        )

        print(f'TF-IDF vs Bigram (P-meas): p-val = {p_val_tfidf_bigram}')
        print(f'TF-IDF vs Bigram (F-meas): p-val = {p_val1_tfidf_bigram}')
        print(f'TF-IDF vs Bigram (T-meas): p-val = {p_val2_tfidf_bigram}')
        
        # 解释p-value的意义
        print("\n=== p-value解释 ===")
        print("p-value < 0.05: 差异具有统计显著性")
        print("p-value < 0.01: 差异具有高度统计显著性")
        print("p-value < 0.001: 差异具有极高度统计显著性")
