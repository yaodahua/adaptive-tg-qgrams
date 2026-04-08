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
import simidf_art
import js_art
'''
使用示例：
参数说明：
--test-gen-budget 测试用例生成预算,默认100
--stop-at-failure 是否在发现故障时停止,测试默认False
--delay 是否引入延迟,默认False
--max-len 最大字符串长度,默认100
--runs-simidf 1000 (方法可替换为其他值、例如: tfidf、bigrams、rand、dist,后面的1000是重复次数)

使用方法：
python test_gen_palindrome.py --max-string-length 100 --runs-simidf 1000 --runs-tfidf 1000 --runs-bigrams 1000 --runs-js 1000
onlymethod用法
python test_gen_palindrome.py --max-string-length 100 --only-method js --runs-js 1000
'''



def random_string(max_len=100, start_char=97, end_char=122):
    length = random.randint(0, max_len)
    s = ""
    for _ in range(length):
        s += chr(random.randint(start_char, end_char))
    return s

# 中文注释：随机生成字符串
def random_gen(test_gen_budget=100000, stop_at_failure=False, delay=False, max_len=100):
    try:
        if stop_at_failure:
            start = time.time()
        f = 0.0
        n = 0
        selected_lengths = []
        while n < test_gen_budget or stop_at_failure:
            s = random_string(max_len)
            n += 1
            selected_lengths.append(len(s))
            if is_palindrome.is_palindrom(s, delay) != is_palindrome.is_palindrom_mu1(s):
                f += 1.0
                # print(f"第 {n} 个测试用例失败: {s}")

                if stop_at_failure:
                    return (n, time.time() - start)
                    
        
        return f / test_gen_budget 
    
    finally:
        if 'selected_lengths' in locals() and len(selected_lengths) > 0:
            avg_length = np.mean(selected_lengths)
            avg_length = round(avg_length, 2)
            max_len_name = f'{max_len}'
            len_fold_name = f'results_length/{max_len_name}'
            os.makedirs(len_fold_name, exist_ok=True)
            with open(f'{len_fold_name}/{max_len_name}_rand_length.csv', 'a') as fw:
                fw.write(f'{avg_length}\n')
            # print("文件写入完成")


# 中文注释：基于距离的自适应随机测试
def ART_dist(
    test_gen_budget=100,
    W_sample_size=10, #候选测试用例集合的大小，默认10，在simulation实验里所有art策略都使用10
    stop_at_failure=False,
    delay=False,
    max_len=100,
):
    try:
        if stop_at_failure:
            start = time.time()
        Z = []
        s = random_string(max_len)
        Z.append(s)
        n = 1
        f = 0.0
        selected_lengths = []
        selected_lengths.append(len(s))
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
            selected_lengths.append(len(s_exec))
            if is_palindrome.is_palindrom(s_exec, delay) != is_palindrome.is_palindrom_mu1(
                s_exec
            ):
                f += 1.0
                
                if stop_at_failure:
                    return (n, time.time() - start)
            Z.append(s_exec)
        
        return f / test_gen_budget 
    finally:
        if 'selected_lengths' in locals() and len(selected_lengths) > 0:
            avg_length = np.mean(selected_lengths)
            avg_length = round(avg_length, 2)
            os.makedirs('results_length', exist_ok=True)
            max_len_name = f'{max_len}'
            len_fold_name = f'results_length/{max_len_name}'
            os.makedirs(len_fold_name, exist_ok=True)
            with open(f'{len_fold_name}/{max_len_name}_dist_length.csv', 'a') as fw:
                fw.write(f'{avg_length}\n')
            # print("文件写入完成")



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
    try:
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
        selected_lengths = []
        selected_lengths.append(len(s))

        if is_palindrome.is_palindrom(s, delay) != is_palindrome.is_palindrom_mu1(s):
            f += 1.0
            # print(f"第 {n} 个测试用例失败: {s}")
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
            selected_lengths.append(len(s_exec))

            if is_palindrome.is_palindrom(s_exec, delay) != is_palindrome.is_palindrom_mu1(
                s_exec
            ):
                f += 1.0
                # print(f"第 {n} 个测试用例失败: {s_exec}")
                if stop_at_failure:
                    return (n, time.time() - start)
            Z.append(s_exec)
            # bigram_count(bigram_dict, s_exec)
            local_bigram_dict = {}
            bigram_count(local_bigram_dict, s_exec)
            ient.store_changes(local_bigram_dict)
        return f / test_gen_budget 
    
    finally:
        if 'selected_lengths' in locals() and len(selected_lengths) > 0:
            avg_length = np.mean(selected_lengths)
            avg_length = round(avg_length, 2)
            max_len_name = f'{max_len}'
            len_fold_name = f'results_length/{max_len_name}'
            os.makedirs(len_fold_name, exist_ok=True)
            with open(f'{len_fold_name}/{max_len_name}_bigram_length.csv', 'a') as fw:
                fw.write(f'{avg_length}\n')
            # print("文件写入完成")


# 中文注释：基于JS散度的自适应随机测试

def ART_js(
    test_gen_budget=100,
    W_sample_size=10,
    stop_at_failure=False,
    delay=False,
    max_len=100,
):
    """使用JS散度的自适应随机测试"""
    try:
        if stop_at_failure:
            start = time.time()
        Z = []
        js_model = js_art.IncrementalJS()
        s = random_string(max_len)
        Z.append(s)
        
        # 初始化：计算第一个测试用例的2-gram频率
        local_bigram_dict = {}
        bigram_count(local_bigram_dict, s)
        js_model.update(local_bigram_dict)
        
        n = 1
        f = 0.0
        selected_lengths = []
        selected_lengths.append(len(s))

        if is_palindrome.is_palindrom(s, delay) != is_palindrome.is_palindrom_mu1(s):
            f += 1.0
            if stop_at_failure:
                return (n, time.time() - start)
        
        while n < test_gen_budget or stop_at_failure:
            W = []
            W_js = []
            
            for i in range(W_sample_size):
                s = random_string(max_len)
                local_bigram_dict = {}
                bigram_count(local_bigram_dict, s)
                js_value = js_model.compute_js(local_bigram_dict)
                W.append(s)
                W_js.append(js_value)
            
            # 选择JS散度最大的候选（与全局分布差异最大）
            s_exec = W[np.argmax(W_js)]
            # max_idx = W_js.index(max(W_js))
            # s_exec = W[max_idx]
            n += 1
            selected_lengths.append(len(s_exec))

            if is_palindrome.is_palindrom(s_exec, delay) != is_palindrome.is_palindrom_mu1(
                s_exec
            ):
                f += 1.0
                if stop_at_failure:
                    return (n, time.time() - start)
            
            Z.append(s_exec)
            
            # 更新全局JS模型
            local_bigram_dict = {}
            bigram_count(local_bigram_dict, s_exec)
            js_model.update(local_bigram_dict)
        
        return f / test_gen_budget 
    
    finally:
        if 'selected_lengths' in locals() and len(selected_lengths) > 0:
            avg_length = np.mean(selected_lengths)
            avg_length = round(avg_length, 2)
            max_len_name = f'{max_len}'
            len_fold_name = f'results_length/{max_len_name}'
            os.makedirs(len_fold_name, exist_ok=True)
            with open(f'{len_fold_name}/{max_len_name}_js_length.csv', 'a') as fw:
                fw.write(f'{avg_length}\n')
            # print("文件写入完成")


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

# 中文注释：基于SimIDF的自适应随机测试
# def ART_simidf(
#     test_gen_budget=100,
#     W_sample_size=10,
#     stop_at_failure=False,
#     delay=False,
#     max_len=100,
# ):
#     """使用SimIDF算法(基于文档频率的TF-IDF)的自适应随机测试"""
#     if stop_at_failure:
#         start = time.time()
    
#     # 重置SimIDF算法状态
#     simidf_art.simidf_art.reset()
    
#     # 初始化：执行第一个随机测试
#     s = random_string(max_len)
#     simidf_art.simidf_art.update_structures(s)
    
#     n = 1
#     f = 0.0
#     selected_lengths = []
#     selected_lengths.append(len(s))

#     if is_palindrome.is_palindrom(s, delay) != is_palindrome.is_palindrom_mu1(s):
#         f += 1.0
#         if stop_at_failure:
#             return (n, time.time() - start)
        
#     while n < test_gen_budget or stop_at_failure:
#         W = []
#         W_diversity = []
        
#         # 生成候选集
#         for i in range(W_sample_size):
#             s = random_string(max_len)
#             # 计算多样性分数（与全局TF-IDF向量的距离）
#             diversity_score = simidf_art.simidf_art.diversity_score(s)
#             W.append(s)
#             W_diversity.append(diversity_score)
        
#         # 选择多样性分数最高的候选（距离最大，即最不相似）
#         s_exec = W[np.argmax(W_diversity)]
#         selected_lengths.append(len(s_exec))

#         n += 1
        
#         if is_palindrome.is_palindrom(s_exec, delay) != is_palindrome.is_palindrom_mu1(s_exec):
#             f += 1.0
#             if stop_at_failure:
#                 return (n, time.time() - start)
        
#         # 更新SimIDF算法结构
#         simidf_art.simidf_art.update_structures(s_exec)
    
    
#     avg_length = np.mean(selected_lengths)
#         #将avg_length保留两位小数，并写入results_length下的simidf_length.csv 文件中,csv文件有1列，记录的是该轮次的测试用例平均长度
#     avg_length = round(avg_length, 2)
#     os.makedirs('results_length', exist_ok=True)
#     with open('results_length/simidf_length.csv', 'a') as fw:
#         fw.write(f'{avg_length}\n')
#     print("文件写入完成")

#     return f / test_gen_budget

def ART_simidf(
    test_gen_budget=100,
    W_sample_size=10,
    stop_at_failure=False,
    delay=False,
    max_len=100,
):
    """使用SimIDF算法(基于文档频率的TF-IDF)的自适应随机测试"""
    try:
        if stop_at_failure:
            start = time.time()
        
        # 重置SimIDF算法状态
        simidf_art.simidf_art.reset()
        
        # 初始化：执行第一个随机测试
        s = random_string(max_len)
        simidf_art.simidf_art.update_structures(s)
        
        n = 1
        f = 0.0
        selected_lengths = []
        selected_lengths.append(len(s))

        if is_palindrome.is_palindrom(s, delay) != is_palindrome.is_palindrom_mu1(s):
            f += 1.0
            # print(f"第 {n} 个测试用例失败: {s}")
            if stop_at_failure:
                return (n, time.time() - start)
            
        while n < test_gen_budget or stop_at_failure:
            W = []
            W_diversity = []
            
            # 生成候选集
            for i in range(W_sample_size):
                s = random_string(max_len)
                # 计算多样性分数（与全局TF-IDF向量的距离）
                diversity_score = simidf_art.simidf_art.diversity_score(s)
                W.append(s)
                W_diversity.append(diversity_score)
            
            # 选择多样性分数最高的候选（距离最大，即最不相似）
            s_exec = W[np.argmax(W_diversity)]
            selected_lengths.append(len(s_exec))

            n += 1
            
            if is_palindrome.is_palindrom(s_exec, delay) != is_palindrome.is_palindrom_mu1(s_exec):
                f += 1.0
                # print(f"第 {n} 个测试用例失败: {s_exec}")
                
                if stop_at_failure:
                    return (n, time.time() - start)
            
            # 更新SimIDF算法结构
            simidf_art.simidf_art.update_structures(s_exec)
        
        return f / test_gen_budget
        
    finally:
        # 无论函数如何返回，这段代码都会执行
        if 'selected_lengths' in locals() and len(selected_lengths) > 0:
            avg_length = np.mean(selected_lengths)
            avg_length = round(avg_length, 2)
            max_len_name = f'{max_len}'
            len_fold_name = f'results_length/{max_len_name}'
            os.makedirs(len_fold_name, exist_ok=True)
            with open(f'{len_fold_name}/{max_len_name}_simidf_length.csv', 'a') as fw:
                fw.write(f'{avg_length}\n')
            # print("文件写入完成")

# 中文注释：计算f-measure和t-measure
def f_t_measure(
    runs_rand=1000, runs_dist=10, runs_bigrams=100, runs_tfidf=100, runs_simidf=100, runs_js=100, delay=False, max_len=100
):
    res_rand = []#记录随机测试的f-measure和t-measure
    print(f'**** Running Rand ({runs_rand}) ****')
    for i in range(runs_rand):
        res_rand.append(random_gen(stop_at_failure=True, delay=delay, max_len=max_len))
        #25轮才输出一次进度
        if (i+1) % 25 == 0:
            print(f"{i+1}/{runs_rand}")
    # res_rand = [random_gen(stop_at_failure=True) for i in range(runs_rand)]
    res_dist = []
    print(f'**** Running Dist ({runs_dist}) ****')
    for i in range(runs_dist):
        res_dist.append(ART_dist(stop_at_failure=True, delay=delay, max_len=max_len))
        #25轮才输出一次进度
        if (i+1) % 25 == 0:
            print(f"{i+1}/{runs_dist}")
    # res_dist = [ART_dist(stop_at_failure=True) for i in range(runs_dist)]
    res_bigrams = []
    print(f'**** Running Bigram ({runs_bigrams}) ****')
    for i in range(runs_bigrams):
        res_bigrams.append(
            ART_bigram(stop_at_failure=True, delay=delay, max_len=max_len)
        )
        #25轮才输出一次进度
        if (i+1) % 25 == 0:
            print(f"{i+1}/{runs_bigrams}")
    # res_bigrams = [ART_bigram(stop_at_failure=True) for i in range(runs_bigrams)]
    res_tfidf = []
    print(f'**** Running TF-IDF ({runs_tfidf}) ****')
    for i in range(runs_tfidf):
        res_tfidf.append(
            ART_tfidf(stop_at_failure=True, delay=delay, max_len=max_len)
        )
        #25轮才输出一次进度
        if (i+1) % 25 == 0:
            print(f"{i+1}/{runs_tfidf}")
    # res_tfidf = [ART_tfidf(stop_at_failure=True) for i in range(runs_tfidf)]
    res_simidf = []
    print(f'**** Running SimIDF ({runs_simidf}) ****')
    for i in range(runs_simidf):
        res_simidf.append(
            ART_simidf(stop_at_failure=True, delay=delay, max_len=max_len)
        )
        #25轮才输出一次进度
        if (i+1) % 25 == 0:
            print(f"{i+1}/{runs_simidf}")
    # res_simidf = [ART_simidf(stop_at_failure=True) for i in range(runs_simidf)]
    res_js = []
    print(f'**** Running JS ({runs_js}) ****')
    for i in range(runs_js):
        res_js.append(
            ART_js(stop_at_failure=True, delay=delay, max_len=max_len)
        )
        #25轮才输出一次进度
        if (i+1) % 25 == 0:
            print(f"{i+1}/{runs_js}")
    # res_js = [ART_js(stop_at_failure=True) for i in range(runs_js)]
    f_rand = 0 if runs_rand == 0 else np.mean([n for n, t in res_rand])
    f_dist = 0 if runs_dist == 0 else np.mean([n for n, t in res_dist])
    f_bigrams = 0 if runs_bigrams == 0 else np.mean([n for n, t in res_bigrams])
    f_tfidf = 0 if runs_tfidf == 0 else np.mean([n for n, t in res_tfidf])
    f_simidf = 0 if runs_simidf == 0 else np.mean([n for n, t in res_simidf])
    f_js = 0 if runs_js == 0 else np.mean([n for n, t in res_js])
    t_rand = 0 if runs_rand == 0 else np.mean([t for n, t in res_rand])
    t_dist = 0 if runs_dist == 0 else np.mean([t for n, t in res_dist])
    t_bigrams = 0 if runs_bigrams == 0 else np.mean([t for n, t in res_bigrams])
    t_tfidf = 0 if runs_tfidf == 0 else np.mean([t for n, t in res_tfidf])
    t_simidf = 0 if runs_simidf == 0 else np.mean([t for n, t in res_simidf])
    t_js = 0 if runs_js == 0 else np.mean([t for n, t in res_js])
    if runs_rand != 0:
        utils.write_f_t_results(res_rand, "rand", max_len, delay)
    if runs_dist != 0:
        utils.write_f_t_results(res_dist, "dist", max_len, delay)
    if runs_bigrams != 0:
        utils.write_f_t_results(res_bigrams, "bigrams", max_len, delay)
    if runs_tfidf != 0:
        utils.write_f_t_results(res_tfidf, "tfidf", max_len, delay)
    if runs_simidf != 0:
        utils.write_f_t_results(res_simidf, "simidf", max_len, delay)
    if runs_js != 0:
        utils.write_f_t_results(res_js, "js", max_len, delay)
    
    return ((f_rand, f_dist, f_bigrams, f_tfidf, f_simidf, f_js), (t_rand, t_dist, t_bigrams, t_tfidf, t_simidf, t_js))

# 中文注释：计算p-measure
def p_measure(
    runs_rand=1000,
    runs_dist=10,
    runs_bigrams=100,
    runs_tfidf=100,
    runs_simidf=100,
    runs_js=100,
    tgen_budget=50,
    delay=False,
    max_len=100,
):
    res_rand = []
    print(f'**** Running Rand ({runs_rand}) ****')
    for i in range(runs_rand):
        res_rand.append(random_gen(test_gen_budget=tgen_budget, max_len=max_len))
        #25轮才输出一次进度
        if (i+1) % 25 == 0:
            print(f"{i+1}/{runs_rand}")
    # res_rand = [random_gen(test_gen_budget=tgen_budget) for i in range(runs_rand)]
    res_dist = []
    print(f'**** Running Dist ({runs_dist}) ****')
    for i in range(runs_dist):
        res_dist.append(ART_dist(test_gen_budget=tgen_budget, max_len=max_len))
        #25轮才输出一次进度
        if (i+1) % 25 == 0:
            print(f"{i+1}/{runs_dist}")
    # res_dist = [ART_dist(test_gen_budget=tgen_budget) for i in range(runs_dist)]
    res_bigrams = []
    print(f'**** Running Bigram ({runs_bigrams}) ****')
    for i in range(runs_bigrams):
        res_bigrams.append(ART_bigram(test_gen_budget=tgen_budget, max_len=max_len))
        #25轮才输出一次进度
        if (i+1) % 25 == 0:
            print(f"{i+1}/{runs_bigrams}")
    # res_bigrams = [ART_bigram(test_gen_budget=tgen_budget) for i in range(runs_bigrams)]
    res_tfidf = []
    print(f'**** Running TF-IDF ({runs_tfidf}) ****')
    for i in range(runs_tfidf):
        res_tfidf.append(ART_tfidf(test_gen_budget=tgen_budget, max_len=max_len))
        #25轮才输出一次进度
        if (i+1) % 25 == 0:
            print(f"{i+1}/{runs_tfidf}")
    # res_tfidf = [ART_tfidf(test_gen_budget=tgen_budget) for i in range(runs_tfidf)]
    res_simidf = []
    print(f'**** Running SimIDF ({runs_simidf}) ****')
    for i in range(runs_simidf):
        res_simidf.append(ART_simidf(test_gen_budget=tgen_budget, max_len=max_len))
        #25轮才输出一次进度
        if (i+1) % 25 == 0:
            print(f"{i+1}/{runs_simidf}")
    # res_simidf = [ART_simidf(test_gen_budget=tgen_budget) for i in range(runs_simidf)]
    res_js = []
    print(f'**** Running JS ({runs_js}) ****')
    for i in range(runs_js):
        res_js.append(ART_js(test_gen_budget=tgen_budget, max_len=max_len))
        #25轮才输出一次进度
        if (i+1) % 25 == 0:
            print(f"{i+1}/{runs_js}")
    # res_js = [ART_js(test_gen_budget=tgen_budget) for i in range(runs_js)]
    p_rand = 0 if runs_rand == 0 else np.mean(res_rand)
    p_dist = 0 if runs_dist == 0 else np.mean(res_dist)
    p_bigrams = 0 if runs_bigrams == 0 else np.mean(res_bigrams)
    p_tfidf = 0 if runs_tfidf == 0 else np.mean(res_tfidf)
    p_simidf = 0 if runs_simidf == 0 else np.mean(res_simidf)
    p_js = 0 if runs_js == 0 else np.mean(res_js)
    if runs_rand != 0:
        utils.write_p_results(res_rand, "rand", max_len, delay)
    if runs_dist != 0:
        utils.write_p_results(res_dist, "dist", max_len, delay)
    if runs_bigrams != 0:
        utils.write_p_results(res_bigrams, "bigrams", max_len, delay)
    if runs_tfidf != 0:
        utils.write_p_results(res_tfidf, "tfidf", max_len, delay)
    if runs_simidf != 0:
        utils.write_p_results(res_simidf, "simidf", max_len, delay)
    if runs_js != 0:
        utils.write_p_results(res_js, "js", max_len, delay)
    
    return (p_rand, p_dist, p_bigrams, p_tfidf, p_simidf, p_js)

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
args.add_argument(
    "--runs-simidf",
    help="Number of runs for ART_simidf (SimIDF 2-grams)",
    type=int,
    default=100,
)
args.add_argument(
    "--runs-js",
    help="Number of runs for ART_js (JS divergence)",
    type=int,
    default=100,
)
args.add_argument(
    "--only-method",
    help="Run only the specified method (rand, dist, bigrams, tfidf, simidf, js)",
    type=str,
    choices=['rand', 'dist', 'bigrams', 'tfidf', 'simidf', 'js'],
    default=None,
)
#args, _ = args.parse_args()
args = args.parse_args() 

# python test_gen_palindrome.py --max-string-length 100 --runs-rand 100 --runs-dist 100 --runs-bigrams 100 --runs-tfidf 100 --runs-simidf 100

if __name__ == "__main__":
    # 66225 ensures failure rate = 1.51e-5 for random generation
    MAX_STR_LENGTH = args.max_string_length
    ADD_DELAY = args.delay
    runs_rand = args.runs_rand
    runs_dist = args.runs_dist
    runs_bigrams = args.runs_bigrams
    runs_tfidf = args.runs_tfidf
    runs_simidf = args.runs_simidf
    runs_js = args.runs_js
    only_method = args.only_method
    
    # 如果指定了only-method，则只运行该方法
    if only_method:
        if only_method == 'rand':
            runs_dist = 0
            runs_bigrams = 0
            runs_tfidf = 0
            runs_simidf = 0
            runs_js = 0
        elif only_method == 'dist':
            runs_rand = 0
            runs_bigrams = 0
            runs_tfidf = 0
            runs_simidf = 0
            runs_js = 0
        elif only_method == 'bigrams':
            runs_rand = 0
            runs_dist = 0
            runs_tfidf = 0
            runs_simidf = 0
            runs_js = 0
        elif only_method == 'tfidf':
            runs_rand = 0
            runs_dist = 0
            runs_bigrams = 0
            runs_simidf = 0
            runs_js = 0
        elif only_method == 'simidf':
            runs_rand = 0
            runs_dist = 0
            runs_bigrams = 0
            runs_tfidf = 0
            runs_js = 0
        elif only_method == 'js':
            runs_rand = 0
            runs_dist = 0
            runs_bigrams = 0
            runs_tfidf = 0
            runs_simidf = 0
        print(f"=== 只运行 {only_method} 方法 ===")
    
    if not os.path.exists('results'):
        os.makedirs('results')
    if ADD_DELAY and not os.path.exists('results_del'):
        os.makedirs('results_del')
    #确保运行次数为非负整数
    assert runs_rand >= 0, "Number of runs for random generation must be non-negative"
    assert runs_dist >= 0, "Number of runs for ART_dist must be non-negative"
    assert runs_bigrams >= 0, "Number of runs for ART_bigrams must be non-negative"
    assert runs_tfidf >= 0, "Number of runs for ART_tfidf must be non-negative"
    assert runs_simidf >= 0, "Number of runs for ART_simidf must be non-negative"
    assert runs_js >= 0, "Number of runs for ART_js must be non-negative"
    
    #中文注释：根据是否添加延迟，设置文件名后缀
    if ADD_DELAY:
        DELAY_SUFFIX = "_del"  # '_del' when delay is true; '' otherwise
    
    #打印当前实验字符串
    print(f"当前实验字符串长度: {MAX_STR_LENGTH}")

    #中文注释：显示当前计算项目
    # 在delay情况下跳过pmeasure的计算
    if not ADD_DELAY:
        print("===== 计算p-measure =====")
        p_measure(
            runs_rand=runs_rand,
            runs_dist=runs_dist,
            runs_bigrams=runs_bigrams,
            runs_tfidf=runs_tfidf,
            runs_simidf=runs_simidf,
            runs_js=runs_js,
            max_len=MAX_STR_LENGTH,

        )
    else:
        print("===== 跳过p-measure计算（delay模式） =====")
    
    print("===== Computing f-measure and t-measure =====")
    f_t_measure(
        runs_rand=runs_rand,
        runs_dist=runs_dist,
        runs_bigrams=runs_bigrams,
        runs_tfidf=runs_tfidf,
        runs_simidf=runs_simidf,
        runs_js=runs_js,
        delay=ADD_DELAY,
        max_len=MAX_STR_LENGTH,
    )
    print("===== 完成 =====")
    if ADD_DELAY:
        print("结果保存/results_del")
    else:
        print("结果保存/results")

    #中文注释：写入统计结果
    utils.write_summary_statistics(delay=ADD_DELAY) # 写入统计结果
