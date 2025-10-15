#!/usr/bin/env python3
"""
高级方法对比工具
功能：
1. 统计单个方法的F-measure, T-measure, P-measure
2. 对比不同方法间的性能指标
3. 进行统计显著性检验
4. 结果输出到compare文件夹中
"""

import os
import sys
import argparse
import pandas as pd
import numpy as np
from scipy.stats import ranksums
from datetime import datetime

def ensure_compare_dir():
    """确保compare目录存在"""
    if not os.path.exists('compare'):
        os.makedirs('compare')
    return 'compare'

def get_method_statistics(method, max_str_length):
    """获取单个方法的统计信息"""
    p_file = f"results/P_measure_{method}_{max_str_length}.csv"
    ft_file = f"results/F_T_measure_{method}_{max_str_length}.csv"
    
    if not os.path.exists(p_file) or not os.path.exists(ft_file):
        return None
    
    # 读取P-measure数据
    p_data = []
    try:
        df_p = pd.read_csv(p_file)
        # 处理列名可能有空格的情况
        p_col = 'P_meas' if 'P_meas' in df_p.columns else 'P_meas '
        p_data = df_p[p_col].tolist()
    except Exception as e:
        print(f"读取P-measure文件失败: {e}")
        return None
    
    # 读取F/T-measure数据
    f_data = []
    t_data = []
    try:
        df_ft = pd.read_csv(ft_file)
        # 处理列名可能有空格的情况
        f_col = 'F_meas' if 'F_meas' in df_ft.columns else 'F_meas '
        t_col = 'T_meas' if 'T_meas' in df_ft.columns else 'T_meas'
        f_data = df_ft[f_col].tolist()
        t_data = df_ft[t_col].tolist()
    except Exception as e:
        print(f"读取F/T-measure文件失败: {e}")
        return None
    
    # 计算统计信息
    stats = {
        'method': method,
        'max_str_length': max_str_length,
        'runs': len(p_data),
        'p_mean': np.mean(p_data) if p_data else 0,
        'p_std': np.std(p_data) if p_data else 0,
        'p_median': np.median(p_data) if p_data else 0,
        'f_mean': np.mean(f_data) if f_data else 0,
        'f_std': np.std(f_data) if f_data else 0,
        'f_median': np.median(f_data) if f_data else 0,
        't_mean': np.mean(t_data) if t_data else 0,
        't_std': np.std(t_data) if t_data else 0,
        't_median': np.median(t_data) if t_data else 0
    }
    
    return stats

def compare_two_methods(method1, method2, max_str_length):
    """对比两种方法"""
    stats1 = get_method_statistics(method1, max_str_length)
    stats2 = get_method_statistics(method2, max_str_length)
    
    if not stats1 or not stats2:
        return None
    
    # 读取原始数据进行统计检验
    p_file1 = f"results/P_measure_{method1}_{max_str_length}.csv"
    p_file2 = f"results/P_measure_{method2}_{max_str_length}.csv"
    ft_file1 = f"results/F_T_measure_{method1}_{max_str_length}.csv"
    ft_file2 = f"results/F_T_measure_{method2}_{max_str_length}.csv"
    
    # P-measure统计检验
    df_p1 = pd.read_csv(p_file1)
    df_p2 = pd.read_csv(p_file2)
    p_col1 = 'P_meas' if 'P_meas' in df_p1.columns else 'P_meas '
    p_col2 = 'P_meas' if 'P_meas' in df_p2.columns else 'P_meas '
    p_data1 = df_p1[p_col1].tolist()
    p_data2 = df_p2[p_col2].tolist()
    p_pvalue = ranksums(p_data1, p_data2).pvalue
    
    # F-measure统计检验
    df_ft1 = pd.read_csv(ft_file1)
    df_ft2 = pd.read_csv(ft_file2)
    f_col1 = 'F_meas' if 'F_meas' in df_ft1.columns else 'F_meas '
    f_col2 = 'F_meas' if 'F_meas' in df_ft2.columns else 'F_meas '
    f_data1 = df_ft1[f_col1].tolist()
    f_data2 = df_ft2[f_col2].tolist()
    f_pvalue = ranksums(f_data1, f_data2).pvalue
    
    # T-measure统计检验
    t_col1 = 'T_meas' if 'T_meas' in df_ft1.columns else 'T_meas'
    t_col2 = 'T_meas' if 'T_meas' in df_ft2.columns else 'T_meas'
    t_data1 = df_ft1[t_col1].tolist()
    t_data2 = df_ft2[t_col2].tolist()
    t_pvalue = ranksums(t_data1, t_data2).pvalue
    
    comparison = {
        'method1': method1,
        'method2': method2,
        'max_str_length': max_str_length,
        'p_pvalue': p_pvalue,
        'f_pvalue': f_pvalue,
        't_pvalue': t_pvalue,
        'stats1': stats1,
        'stats2': stats2
    }
    
    return comparison

def generate_single_method_report(stats, output_dir):
    """生成单个方法的报告"""
    method = stats['method']
    max_len = stats['max_str_length']
    
    filename = f"{output_dir}/single_method_{method}_{max_len}.txt"
    
    with open(filename, 'w') as f:
        f.write(f"=== {method.upper()} 方法性能统计报告 ===\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"最大字符串长度: {max_len}\n")
        f.write(f"运行次数: {stats['runs']}\n\n")
        
        f.write("=== P-measure 统计 ===\n")
        f.write(f"平均值: {stats['p_mean']:.6f}\n")
        f.write(f"标准差: {stats['p_std']:.6f}\n")
        f.write(f"中位数: {stats['p_median']:.6f}\n\n")
        
        f.write("=== F-measure 统计 ===\n")
        f.write(f"平均值: {stats['f_mean']:.6f}\n")
        f.write(f"标准差: {stats['f_std']:.6f}\n")
        f.write(f"中位数: {stats['f_median']:.6f}\n\n")
        
        f.write("=== T-measure 统计 ===\n")
        f.write(f"平均值: {stats['t_mean']:.6f}\n")
        f.write(f"标准差: {stats['t_std']:.6f}\n")
        f.write(f"中位数: {stats['t_median']:.6f}\n")
    
    print(f"单个方法报告已保存: {filename}")
    return filename

def generate_comparison_report(comparison, output_dir):
    """生成对比报告"""
    method1 = comparison['method1']
    method2 = comparison['method2']
    max_len = comparison['max_str_length']
    
    filename = f"{output_dir}/comparison_{method1}_vs_{method2}_{max_len}.txt"
    
    with open(filename, 'w') as f:
        f.write(f"=== {method1.upper()} vs {method2.upper()} 对比报告 ===\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"最大字符串长度: {max_len}\n\n")
        
        # 性能指标对比
        f.write("=== 性能指标对比 ===\n")
        f.write(f"指标\t\t{method1}\t\t{method2}\t\t差异\n")
        
        # P-measure对比
        p_diff = comparison['stats2']['p_mean'] - comparison['stats1']['p_mean']
        p_diff_pct = (p_diff / comparison['stats1']['p_mean']) * 100 if comparison['stats1']['p_mean'] != 0 else 0
        f.write(f"P-measure\t{comparison['stats1']['p_mean']:.6f}\t{comparison['stats2']['p_mean']:.6f}\t{p_diff:+.6f} ({p_diff_pct:+.2f}%)\n")
        
        # F-measure对比
        f_diff = comparison['stats2']['f_mean'] - comparison['stats1']['f_mean']
        f_diff_pct = (f_diff / comparison['stats1']['f_mean']) * 100 if comparison['stats1']['f_mean'] != 0 else 0
        f.write(f"F-measure\t{comparison['stats1']['f_mean']:.6f}\t{comparison['stats2']['f_mean']:.6f}\t{f_diff:+.6f} ({f_diff_pct:+.2f}%)\n")
        
        # T-measure对比
        t_diff = comparison['stats2']['t_mean'] - comparison['stats1']['t_mean']
        t_diff_pct = (t_diff / comparison['stats1']['t_mean']) * 100 if comparison['stats1']['t_mean'] != 0 else 0
        f.write(f"T-measure\t{comparison['stats1']['t_mean']:.6f}\t{comparison['stats2']['t_mean']:.6f}\t{t_diff:+.6f} ({t_diff_pct:+.2f}%)\n\n")
        
        # 统计显著性检验结果
        f.write("=== 统计显著性检验 ===\n")
        f.write(f"P-measure p值: {comparison['p_pvalue']:.6f}\n")
        f.write(f"F-measure p值: {comparison['f_pvalue']:.6f}\n")
        f.write(f"T-measure p值: {comparison['t_pvalue']:.6f}\n\n")
        
        # 显著性判断
        f.write("=== 显著性判断 (p < 0.05为显著) ===\n")
        
        def get_significance(pvalue):
            if pvalue < 0.001:
                return "极高度显著 (p < 0.001)"
            elif pvalue < 0.01:
                return "高度显著 (p < 0.01)"
            elif pvalue < 0.05:
                return "显著 (p < 0.05)"
            else:
                return "不显著"
        
        f.write(f"P-measure: {get_significance(comparison['p_pvalue'])}\n")
        f.write(f"F-measure: {get_significance(comparison['f_pvalue'])}\n")
        f.write(f"T-measure: {get_significance(comparison['t_pvalue'])}\n\n")
        
        # 综合结论
        f.write("=== 综合结论 ===\n")
        significant_metrics = []
        if comparison['p_pvalue'] < 0.05:
            significant_metrics.append("P-measure")
        if comparison['f_pvalue'] < 0.05:
            significant_metrics.append("F-measure")
        if comparison['t_pvalue'] < 0.05:
            significant_metrics.append("T-measure")
        
        if significant_metrics:
            f.write(f"{method1}和{method2}在{', '.join(significant_metrics)}上存在统计显著性差异。\n")
        else:
            f.write(f"{method1}和{method2}在所有指标上均无统计显著性差异。\n")
    
    print(f"对比报告已保存: {filename}")
    return filename

def generate_summary_csv(all_stats, comparisons, output_dir):
    """生成汇总CSV文件"""
    # 单个方法统计汇总
    single_filename = f"{output_dir}/single_methods_summary.csv"
    
    # 检查文件是否存在，如果存在则追加，否则创建新文件
    file_exists = os.path.exists(single_filename)
    
    with open(single_filename, 'a' if file_exists else 'w') as f:
        if not file_exists:
            f.write("Method,MaxLength,Runs,P_Mean,P_Std,P_Median,F_Mean,F_Std,F_Median,T_Mean,T_Std,T_Median\n")
        for stats in all_stats:
            # 检查是否已存在相同的方法和长度组合
            existing_entry = False
            if file_exists:
                try:
                    df_existing = pd.read_csv(single_filename)
                    existing_entries = df_existing[(df_existing['Method'] == stats['method']) & 
                                                 (df_existing['MaxLength'] == stats['max_str_length'])]
                    if not existing_entries.empty:
                        existing_entry = True
                except:
                    pass
            
            # 如果不存在相同条目，则写入
            if not existing_entry:
                f.write(f"{stats['method']},{stats['max_str_length']},{stats['runs']},")
                f.write(f"{stats['p_mean']:.6f},{stats['p_std']:.6f},{stats['p_median']:.6f},")
                f.write(f"{stats['f_mean']:.6f},{stats['f_std']:.6f},{stats['f_median']:.6f},")
                f.write(f"{stats['t_mean']:.6f},{stats['t_std']:.6f},{stats['t_median']:.6f}\n")
    
    # 对比结果汇总
    comparison_filename = f"{output_dir}/comparisons_summary.csv"
    
    # 检查文件是否存在，如果存在则追加，否则创建新文件
    file_exists = os.path.exists(comparison_filename)
    
    with open(comparison_filename, 'a' if file_exists else 'w') as f:
        if not file_exists:
            f.write("Method1,Method2,MaxLength,P_Pvalue,F_Pvalue,T_Pvalue,P_Significant,F_Significant,T_Significant\n")
        for comp in comparisons:
            # 检查是否已存在相同的方法对和长度组合
            existing_entry = False
            if file_exists:
                try:
                    df_existing = pd.read_csv(comparison_filename)
                    existing_entries = df_existing[(df_existing['Method1'] == comp['method1']) & 
                                                 (df_existing['Method2'] == comp['method2']) & 
                                                 (df_existing['MaxLength'] == comp['max_str_length'])]
                    if not existing_entries.empty:
                        existing_entry = True
                except:
                    pass
            
            # 如果不存在相同条目，则写入
            if not existing_entry:
                f.write(f"{comp['method1']},{comp['method2']},{comp['max_str_length']},")
                f.write(f"{comp['p_pvalue']:.6f},{comp['f_pvalue']:.6f},{comp['t_pvalue']:.6f},")
                f.write(f"{comp['p_pvalue'] < 0.05},{comp['f_pvalue'] < 0.05},{comp['t_pvalue'] < 0.05}\n")
    
    print(f"汇总CSV文件已保存: {single_filename}, {comparison_filename}")
    return single_filename, comparison_filename

def main():
    parser = argparse.ArgumentParser(description='高级方法对比工具')
    parser.add_argument('--max-string-length', type=int, default=100, 
                       choices=[100, 1000, 10000, 66225],
                       help='最大字符串长度 (默认: 100)')
    parser.add_argument('--methods', nargs='+', 
                       choices=['rand', 'dist', 'bigrams', 'tfidf', 'simidf'],
                       help='指定要分析的方法列表')
    parser.add_argument('--all-methods', action='store_true',
                       help='分析所有可用方法')
    parser.add_argument('--compare-pairs', nargs='+', 
                       help='指定要对比的方法对，格式: method1:method2')
    parser.add_argument('--compare-all', action='store_true',
                       help='对比所有方法组合')
    
    args = parser.parse_args()
    
    # 确保results目录存在
    if not os.path.exists('results'):
        print("错误: results目录不存在，请先运行测试生成结果")
        sys.exit(1)
    
    # 确保compare目录存在
    output_dir = ensure_compare_dir()
    
    max_str_length = args.max_string_length
    
    # 所有支持的方法
    all_available_methods = ['rand', 'dist', 'bigrams', 'tfidf', 'simidf']
    
    # 确定要分析的方法
    if args.all_methods:
        methods_to_analyze = all_available_methods
    elif args.methods:
        methods_to_analyze = args.methods
    else:
        methods_to_analyze = all_available_methods
    
    print(f"=== 开始分析 (最大字符串长度: {max_str_length}) ===")
    
    # 统计单个方法
    all_stats = []
    for method in methods_to_analyze:
        print(f"分析 {method} 方法...")
        stats = get_method_statistics(method, max_str_length)
        if stats:
            all_stats.append(stats)
            generate_single_method_report(stats, output_dir)
        else:
            print(f"警告: {method} 方法结果文件不完整，跳过")
    
    # 方法对比
    comparisons = []
    
    # 确定要对比的方法对
    if args.compare_all:
        # 对比所有方法组合
        for i in range(len(methods_to_analyze)):
            for j in range(i + 1, len(methods_to_analyze)):
                method1 = methods_to_analyze[i]
                method2 = methods_to_analyze[j]
                print(f"对比 {method1} vs {method2}...")
                comp = compare_two_methods(method1, method2, max_str_length)
                if comp:
                    comparisons.append(comp)
                    generate_comparison_report(comp, output_dir)
    elif args.compare_pairs:
        # 对比指定方法对
        for pair in args.compare_pairs:
            if ':' not in pair:
                print(f"错误: 无效的方法对格式: {pair}，应使用 method1:method2 格式")
                continue
            method1, method2 = pair.split(':')
            if method1 not in all_available_methods or method2 not in all_available_methods:
                print(f"错误: 无效的方法名称: {method1} 或 {method2}")
                continue
            print(f"对比 {method1} vs {method2}...")
            comp = compare_two_methods(method1, method2, max_str_length)
            if comp:
                comparisons.append(comp)
                generate_comparison_report(comp, output_dir)
    else:
        # 默认对比TF-IDF和Bigram
        if 'tfidf' in methods_to_analyze and 'bigrams' in methods_to_analyze:
            print("对比 tfidf vs bigrams...")
            comp = compare_two_methods('tfidf', 'bigrams', max_str_length)
            if comp:
                comparisons.append(comp)
                generate_comparison_report(comp, output_dir)
    
    # 生成汇总文件
    if all_stats or comparisons:
        generate_summary_csv(all_stats, comparisons, output_dir)
    
    print(f"\n=== 分析完成 ===")
    print(f"结果文件保存在: {output_dir}/ 目录")
    print(f"共分析了 {len(all_stats)} 个方法，进行了 {len(comparisons)} 次对比")

'''
使用示例：
分析所有方法，对比所有组合：
python advanced_comparison.py --max-string-length 1000 --all-methods --compare-all
会生成 single_methods_summary.csv 和 comparisons_summary.csv 两个汇总文件

对比指定方法对：
python advanced_comparison.py --compare-pairs simidf:bigrams tfidf:bigrams --max-string-length 1000
会生成 simidf_vs_bigrams.csv 和 tfidf_vs_bigrams.csv 两个对比文件，以及 comparisons_summary.csv 对比文件

分析指定方法：
python advanced_comparison.py --methods simidf bigrams tfidf --max-string-length 1000
会生成 simidf.csv, bigrams.csv, tfidf.csv 三个文件

对比所有方法组合：
python advanced_comparison.py --max-string-length 1000 --all-methods --compare-all
会生成/更新 comparisons_summary.csv 对比文件

生成的文件保存在 compare/ 目录下
comparisons_summary.csv 对比的是显著性差异，即是否存在统计显著的差异

'''

if __name__ == "__main__":
    main()
    