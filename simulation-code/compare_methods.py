#!/usr/bin/env python3
"""
独立的方法对比工具
支持基于现有结果文件进行方法对比，无需重新运行测试
"""

import os
import sys
import argparse
import pandas as pd
from utils import compare_P_meas, compare_F_T_meas

def check_file_exists(file_path, method_name):
    """检查文件是否存在，如果不存在则提示"""
    if not os.path.exists(file_path):
        print(f"警告: {method_name} 结果文件不存在: {file_path}")
        return False
    return True

def compare_two_methods(method1, method2, max_str_length):
    """对比两种方法"""
    print(f"\n===== {method1.upper()} vs {method2.upper()} 统计显著性检验 =====")
    
    # 构建文件路径
    method1_p_file = f"results/P_measure_{method1}_{max_str_length}.csv"
    method1_ft_file = f"results/F_T_measure_{method1}_{max_str_length}.csv"
    method2_p_file = f"results/P_measure_{method2}_{max_str_length}.csv"
    method2_ft_file = f"results/F_T_measure_{method2}_{max_str_length}.csv"
    
    # 检查文件存在性
    files_exist = True
    files_exist &= check_file_exists(method1_p_file, method1)
    files_exist &= check_file_exists(method1_ft_file, method1)
    files_exist &= check_file_exists(method2_p_file, method2)
    files_exist &= check_file_exists(method2_ft_file, method2)
    
    if not files_exist:
        print(f"无法进行 {method1} vs {method2} 对比，缺少结果文件")
        return
    
    # 进行P-measure对比
    try:
        p_val = compare_P_meas(method1_p_file, method2_p_file)
        print(f"P-measure对比 p值: {p_val:.6f}")
        if p_val < 0.05:
            print("  → 统计显著性差异 (p < 0.05)")
        else:
            print("  → 无统计显著性差异")
    except Exception as e:
        print(f"P-measure对比失败: {e}")
    
    # 进行F/T-measure对比
    try:
        p_val1, p_val2 = compare_F_T_meas(method1_ft_file, method2_ft_file)
        print(f"F-measure对比 p值: {p_val1:.6f}")
        if p_val1 < 0.05:
            print("  → F-measure有统计显著性差异 (p < 0.05)")
        else:
            print("  → F-measure无统计显著性差异")
        
        print(f"T-measure对比 p值: {p_val2:.6f}")
        if p_val2 < 0.05:
            print("  → T-measure有统计显著性差异 (p < 0.05)")
        else:
            print("  → T-measure无统计显著性差异")
    except Exception as e:
        print(f"F/T-measure对比失败: {e}")

def generate_comprehensive_report(methods, max_str_length):
    """生成综合对比报告"""
    print(f"\n===== 综合对比报告 (最大字符串长度: {max_str_length}) =====")
    
    # 检查所有方法的结果文件
    available_methods = []
    for method in methods:
        p_file = f"results/P_measure_{method}_{max_str_length}.csv"
        ft_file = f"results/F_T_measure_{method}_{max_str_length}.csv"
        
        if os.path.exists(p_file) and os.path.exists(ft_file):
            available_methods.append(method)
            print(f"✓ {method} 结果文件存在")
        else:
            print(f"✗ {method} 结果文件不完整")
    
    if len(available_methods) < 2:
        print("可用方法不足2个，无法生成对比报告")
        return
    
    # 进行两两对比
    for i in range(len(available_methods)):
        for j in range(i + 1, len(available_methods)):
            compare_two_methods(available_methods[i], available_methods[j], max_str_length)

def main():
    parser = argparse.ArgumentParser(description='方法对比工具')
    parser.add_argument('--max-string-length', type=int, default=100, 
                       help='最大字符串长度 (默认: 100)')
    parser.add_argument('--compare', nargs='+', choices=['rand', 'dist', 'bigrams', 'tfidf', 'simidf'],
                       help='指定要对比的方法列表')
    parser.add_argument('--all-methods', action='store_true',
                       help='对比所有可用方法')
    
    args = parser.parse_args()
    
    # 确保results目录存在
    if not os.path.exists('results'):
        print("错误: results目录不存在，请先运行测试生成结果")
        sys.exit(1)
    
    max_str_length = args.max_string_length
    
    # 所有支持的方法
    all_methods = ['rand', 'dist', 'bigrams', 'tfidf', 'simidf']
    
    if args.all_methods:
        # 对比所有方法
        generate_comprehensive_report(all_methods, max_str_length)
    elif args.compare:
        # 对比指定方法
        if len(args.compare) < 2:
            print("错误: 需要至少指定2个方法进行对比")
            sys.exit(1)
        generate_comprehensive_report(args.compare, max_str_length)
    else:
        # 默认对比TF-IDF和Bigram
        compare_two_methods('tfidf', 'bigrams', max_str_length)

if __name__ == "__main__":
    main()