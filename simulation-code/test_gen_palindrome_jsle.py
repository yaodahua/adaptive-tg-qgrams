import random
import is_palindrome
import time
import numpy as np
import argparse
import os
import jsle_art
from jsle_art import BoundaryScheme
import utils



def random_string(max_len=100, start_char=97, end_char=122):
    """随机生成字符串"""
    length = random.randint(0, max_len)
    s = ""
    for _ in range(length):
        s += chr(random.randint(start_char, end_char))
    return s


# 中文注释：基于JSLE-ART的自适应随机测试
def ART_jsle(
    test_gen_budget=100,
    W_sample_size=10,
    stop_at_failure=False,
    delay=False,
    max_len=100,
    boundary_scheme=BoundaryScheme.SCHEME_A,
    q=2
):
    """
    JSLE-ART算法实现
    
    Args:
        test_gen_budget: 测试用例生成预算
        W_sample_size: 候选集大小
        stop_at_failure: 是否在发现故障时停止
        delay: 是否引入延迟
        max_len: 最大字符串长度
        boundary_scheme: 边界编码方案
        q: Q-gram大小
    """
    try:
        if stop_at_failure:
            start = time.time()
        
        # 初始化JSLE-ART模型
        jsle_model = jsle_art.JSLE_ART(boundary_scheme=boundary_scheme, q=q)
        
        # 生成初始测试用例
        t0 = random_string(max_len)
        jsle_model.update(t0)
        
        n = 1
        f = 0.0
        selected_lengths = []
        selected_lengths.append(len(t0))
        
        # 执行初始测试用例
        if is_palindrome.is_palindrom(t0, delay) != is_palindrome.is_palindrom_mu1(t0):
            f += 1.0
            if stop_at_failure:
                return (n, time.time() - start)
        
        while n < test_gen_budget or stop_at_failure:
            # 生成候选集
            W = [random_string(max_len) for _ in range(W_sample_size)]
            
            # 选择最优候选
            best_candidate, js_score = jsle_model.select_test_case(W)
            
            # 执行选中的测试用例
            n += 1
            selected_lengths.append(len(best_candidate))
            
            if is_palindrome.is_palindrom(best_candidate, delay) != is_palindrome.is_palindrom_mu1(best_candidate):
                f += 1.0
                if stop_at_failure:
                    return (n, time.time() - start)
            
            # 更新模型状态
            jsle_model.update(best_candidate)
        
        return f / test_gen_budget
    
    finally:
        # # 记录平均长度
        # if 'selected_lengths' in locals() and len(selected_lengths) > 0:
        #     avg_length = np.mean(selected_lengths)
        #     avg_length = round(avg_length, 2)
            
        #     # 根据边界方案创建不同的文件名
        #     scheme_name = boundary_scheme.value
        #     max_len_name = f'{max_len}'
        #     len_fold_name = f'results_length/{max_len_name}'
            
        #     os.makedirs(len_fold_name, exist_ok=True)
        #     with open(f'{len_fold_name}/{max_len_name}_jsle_{scheme_name}_length.csv', 'a') as fw:
        #         fw.write(f'{avg_length}\n')
        pass


# 中文注释：计算f-measure和t-measure
def f_t_measure_jsle(
    runs_jsle_a=100, runs_jsle_b=100, runs_jsle_c=100, delay=False, max_len=100
):
    """计算JSLE-ART方法的f-measure和t-measure"""
    res_jsle_a = []
    if runs_jsle_a > 0:
        print(f'**** Running JSLE-A ({runs_jsle_a}) ****')
        for i in range(runs_jsle_a):
            res_jsle_a.append(ART_jsle(stop_at_failure=True, delay=delay, max_len=max_len, boundary_scheme=BoundaryScheme.SCHEME_A))
            if (i+1) % 25 == 0:
                print(f"{i+1}/{runs_jsle_a}")
    
    res_jsle_b = []
    if runs_jsle_b > 0:
        print(f'**** Running JSLE-B ({runs_jsle_b}) ****')
        for i in range(runs_jsle_b):
            res_jsle_b.append(ART_jsle(stop_at_failure=True, delay=delay, max_len=max_len, boundary_scheme=BoundaryScheme.SCHEME_B))
            if (i+1) % 25 == 0:
                print(f"{i+1}/{runs_jsle_b}")
    
    res_jsle_c = []
    if runs_jsle_c > 0:
        print(f'**** Running JSLE-C ({runs_jsle_c}) ****')
        for i in range(runs_jsle_c):
            res_jsle_c.append(ART_jsle(stop_at_failure=True, delay=delay, max_len=max_len, boundary_scheme=BoundaryScheme.SCHEME_C))
            if (i+1) % 25 == 0:
                print(f"{i+1}/{runs_jsle_c}")
    
    # 计算f-measure和t-measure
    f_jsle_a = 0 if runs_jsle_a == 0 else np.mean([n for n, t in res_jsle_a])
    f_jsle_b = 0 if runs_jsle_b == 0 else np.mean([n for n, t in res_jsle_b])
    f_jsle_c = 0 if runs_jsle_c == 0 else np.mean([n for n, t in res_jsle_c])
    t_jsle_a = 0 if runs_jsle_a == 0 else np.mean([t for n, t in res_jsle_a])
    t_jsle_b = 0 if runs_jsle_b == 0 else np.mean([t for n, t in res_jsle_b])
    t_jsle_c = 0 if runs_jsle_c == 0 else np.mean([t for n, t in res_jsle_c])
    
    # 使用utils保存结果
    if runs_jsle_a != 0:
        utils.write_f_t_results(res_jsle_a, "jsle_a", max_len, delay)
    if runs_jsle_b != 0:
        utils.write_f_t_results(res_jsle_b, "jsle_b", max_len, delay)
    if runs_jsle_c != 0:
        utils.write_f_t_results(res_jsle_c, "jsle_c", max_len, delay)
    
    return ((f_jsle_a, f_jsle_b, f_jsle_c), (t_jsle_a, t_jsle_b, t_jsle_c))


# 中文注释：计算p-measure
def p_measure_jsle(
    runs_jsle_a=100,
    runs_jsle_b=100,
    runs_jsle_c=100,
    tgen_budget=50,
    delay=False,
    max_len=100,
):
    """计算JSLE-ART方法的p-measure"""
    res_jsle_a = []
    if runs_jsle_a > 0:
        print(f'**** Running JSLE-A ({runs_jsle_a}) ****')
        for i in range(runs_jsle_a):
            res_jsle_a.append(ART_jsle(test_gen_budget=tgen_budget, delay=delay, max_len=max_len, boundary_scheme=BoundaryScheme.SCHEME_A))
            if (i+1) % 25 == 0:
                print(f"{i+1}/{runs_jsle_a}")
    
    res_jsle_b = []
    if runs_jsle_b > 0:
        print(f'**** Running JSLE-B ({runs_jsle_b}) ****')
        for i in range(runs_jsle_b):
            res_jsle_b.append(ART_jsle(test_gen_budget=tgen_budget, delay=delay, max_len=max_len, boundary_scheme=BoundaryScheme.SCHEME_B))
            if (i+1) % 25 == 0:
                print(f"{i+1}/{runs_jsle_b}")
    
    res_jsle_c = []
    if runs_jsle_c > 0:
        print(f'**** Running JSLE-C ({runs_jsle_c}) ****')
        for i in range(runs_jsle_c):
            res_jsle_c.append(ART_jsle(test_gen_budget=tgen_budget, delay=delay, max_len=max_len, boundary_scheme=BoundaryScheme.SCHEME_C))
            if (i+1) % 25 == 0:
                print(f"{i+1}/{runs_jsle_c}")
    
    p_jsle_a = 0 if runs_jsle_a == 0 else np.mean(res_jsle_a)
    p_jsle_b = 0 if runs_jsle_b == 0 else np.mean(res_jsle_b)
    p_jsle_c = 0 if runs_jsle_c == 0 else np.mean(res_jsle_c)


    # 使用utils保存结果
    if runs_jsle_a != 0:
        utils.write_p_results(res_jsle_a, "jsle_a", max_len, delay)
    if runs_jsle_b != 0:
        utils.write_p_results(res_jsle_b, "jsle_b", max_len, delay)
    if runs_jsle_c != 0:
        utils.write_p_results(res_jsle_c, "jsle_c", max_len, delay)
    
    return (p_jsle_a, p_jsle_b, p_jsle_c)



args = argparse.ArgumentParser(description='JSLE-ART测试生成器')
args.add_argument('--max-string-length', type=int, default=100, help='最大字符串长度',choices=[100, 1000, 10000, 66225],)
args.add_argument('--test-gen-budget', type=int, default=100, help='测试用例生成预算')
args.add_argument('--stop-at-failure', action='store_true', help='是否在发现故障时停止')
args.add_argument('--delay', action='store_true', help='是否引入延迟', default=False)
args.add_argument('--only-method', type=str, choices=['jsle_a', 'jsle_b', 'jsle_c'], help='只运行指定方法')
args.add_argument('--runs-jsle-a', type=int, default=0, help='JSLE-ART Scheme A重复次数')
args.add_argument('--runs-jsle-b', type=int, default=0, help='JSLE-ART Scheme B重复次数')
args.add_argument('--runs-jsle-c', type=int, default=0, help='JSLE-ART Scheme C重复次数')
# args.add_argument('--f-t-measure', action='store_true', help='计算f-measure和t-measure')
# args.add_argument('--p-measure', action='store_true', help='计算p-measure')
# args.add_argument('--tgen-budget', type=int, default=50, help='p-measure测试预算')

args = args.parse_args()

# python test_gen_palindrome_jsle.py --max-string-length 100 --runs-jsle-a 100 --runs-jsle-b 100 --runs-jsle-c 100 

if __name__ == "__main__":
    MAX_STR_LENGTH = args.max_string_length
    ADD_DELAY = args.delay
    only_method = args.only_method
    runs_jsle_a = args.runs_jsle_a
    runs_jsle_b = args.runs_jsle_b
    runs_jsle_c = args.runs_jsle_c
    # tgen_budget = args.tgen_budget
    if only_method :
        if only_method == 'jsle_a':
            runs_jsle_b = 0
            runs_jsle_c = 0
        elif only_method == 'jsle_b':
            runs_jsle_a = 0
            runs_jsle_c = 0
        elif only_method == 'jsle_c':
            runs_jsle_a = 0
            runs_jsle_b = 0
        print(f"=== 只运行 {only_method} 方法 ===")
    
    if not os.path.exists('results'):
        os.makedirs('results')
    if ADD_DELAY and not os.path.exists('results_del'):
        os.makedirs('results_del')
    
    assert runs_jsle_a >=0, "runs_jsle_a 必须大于等于0"
    assert runs_jsle_b >=0, "runs_jsle_b 必须大于等于0"
    assert runs_jsle_c >=0, "runs_jsle_c 必须大于等于0"
    
    if ADD_DELAY:
        DELAY_SUFFIX = "_del"
    
    #打印当前实验字符串
    print(f"当前实验字符串长度: {MAX_STR_LENGTH}")

    if not ADD_DELAY:
        print("===== 计算p-measure =====")
        p_measure_jsle(
            runs_jsle_a=runs_jsle_a,
            runs_jsle_b=runs_jsle_b,
            runs_jsle_c=runs_jsle_c,
            # delay=ADD_DELAY,
            max_len=MAX_STR_LENGTH
        )
    else:   
        print("===== delay模式下跳过p-measure计算 =====")

    print("===== Computing f-measure and t-measure =====")
    f_t_measure_jsle(
        runs_jsle_a=runs_jsle_a,
        runs_jsle_b=runs_jsle_b,
        runs_jsle_c=runs_jsle_c,
        delay=ADD_DELAY,
        max_len=MAX_STR_LENGTH
    )
    print("===== 计算完成 =====")
    if ADD_DELAY:
        print("结果保存/results_del")
    else:
        print("结果保存/results")

    utils.write_summary_statistics(delay=ADD_DELAY)
# def main():
#     """主函数，支持命令行参数"""
#     parser = argparse.ArgumentParser(description='JSLE-ART测试生成器')
#     parser.add_argument('--max-string-length', type=int, default=100, help='最大字符串长度')
#     parser.add_argument('--test-gen-budget', type=int, default=100, help='测试用例生成预算')
#     parser.add_argument('--stop-at-failure', action='store_true', help='是否在发现故障时停止')
#     parser.add_argument('--delay', action='store_true', help='是否引入延迟')
#     parser.add_argument('--only-method', type=str, choices=['jsle_a', 'jsle_b', 'jsle_c'], help='只运行指定方法')
#     parser.add_argument('--runs-jsle-a', type=int, default=0, help='JSLE-ART Scheme A重复次数')
#     parser.add_argument('--runs-jsle-b', type=int, default=0, help='JSLE-ART Scheme B重复次数')
#     parser.add_argument('--runs-jsle-c', type=int, default=0, help='JSLE-ART Scheme C重复次数')
#     parser.add_argument('--f-t-measure', action='store_true', help='计算f-measure和t-measure')
#     parser.add_argument('--p-measure', action='store_true', help='计算p-measure')
#     parser.add_argument('--tgen-budget', type=int, default=50, help='p-measure测试预算')
    
#     args = parser.parse_args()
    
#     max_len = args.max_string_length
#     test_gen_budget = args.test_gen_budget
#     stop_at_failure = args.stop_at_failure
#     delay = args.delay
    
#     # 创建结果目录
#     os.makedirs('results', exist_ok=True)
#     os.makedirs('results_length', exist_ok=True)
    
#     if args.f_t_measure:
#         # 计算f-measure和t-measure
#         f_t_measure_jsle(
#             runs_jsle_a=args.runs_jsle_a,
#             runs_jsle_b=args.runs_jsle_b,
#             runs_jsle_c=args.runs_jsle_c,
#             delay=delay,
#             max_len=max_len
#         )
#     elif args.p_measure:
#         # 计算p-measure
#         p_measure_jsle(
#             runs_jsle_a=args.runs_jsle_a,
#             runs_jsle_b=args.runs_jsle_b,
#             runs_jsle_c=args.runs_jsle_c,
#             tgen_budget=args.tgen_budget,
#             delay=delay,
#             max_len=max_len
#         )
#     else:
#         # 运行指定方法或所有方法
#         methods_to_run = []
        
#         if args.only_method:
#             if args.only_method == 'jsle_a':
#                 methods_to_run.append(('JSLE-ART Scheme A', BoundaryScheme.SCHEME_A, args.runs_jsle_a or 1000))
#             elif args.only_method == 'jsle_b':
#                 methods_to_run.append(('JSLE-ART Scheme B', BoundaryScheme.SCHEME_B, args.runs_jsle_b or 1000))
#             elif args.only_method == 'jsle_c':
#                 methods_to_run.append(('JSLE-ART Scheme C', BoundaryScheme.SCHEME_C, args.runs_jsle_c or 1000))
#         else:
#             if args.runs_jsle_a > 0:
#                 methods_to_run.append(('JSLE-ART Scheme A', BoundaryScheme.SCHEME_A, args.runs_jsle_a))
#             if args.runs_jsle_b > 0:
#                 methods_to_run.append(('JSLE-ART Scheme B', BoundaryScheme.SCHEME_B, args.runs_jsle_b))
#             if args.runs_jsle_c > 0:
#                 methods_to_run.append(('JSLE-ART Scheme C', BoundaryScheme.SCHEME_C, args.runs_jsle_c))
        
#         if not methods_to_run:
#             # 默认运行所有方法各1000次
#             methods_to_run = [
#                 ('JSLE-ART Scheme A', BoundaryScheme.SCHEME_A, 1000),
#                 ('JSLE-ART Scheme B', BoundaryScheme.SCHEME_B, 1000),
#                 ('JSLE-ART Scheme C', BoundaryScheme.SCHEME_C, 1000)
#             ]
        
#         for method_name, scheme, runs in methods_to_run:
#             print(f"\n开始运行 {method_name}，重复次数: {runs}")
            
#             failures = []
#             for i in range(runs):
#                 if i % 100 == 0:
#                     print(f"进度: {i}/{runs}")
                
#                 failure_rate = ART_jsle(
#                     test_gen_budget=test_gen_budget,
#                     W_sample_size=10,
#                     stop_at_failure=stop_at_failure,
#                     delay=delay,
#                     max_len=max_len,
#                     boundary_scheme=scheme,
#                     q=2
#                 )
#                 failures.append(failure_rate)
            
#             # 保存结果
#             avg_failure = np.mean(failures)
#             std_failure = np.std(failures)
            
#             scheme_name = scheme.value
#             result_file = f'results/{scheme_name}_failure_rate.txt'
            
#             with open(result_file, 'a') as f:
#                 f.write(f"方法: {method_name}\n")
#                 f.write(f"测试预算: {test_gen_budget}\n")
#                 f.write(f"最大长度: {max_len}\n")
#                 f.write(f"重复次数: {runs}\n")
#                 f.write(f"平均故障率: {avg_failure:.6f}\n")
#                 f.write(f"标准差: {std_failure:.6f}\n")
#                 f.write("-" * 50 + "\n")
            
#             print(f"{method_name} 完成:")
#             print(f"  平均故障率: {avg_failure:.6f}")
#             print(f"  标准差: {std_failure:.6f}")


