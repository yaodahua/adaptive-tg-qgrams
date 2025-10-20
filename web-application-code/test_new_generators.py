#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'web-application-code'))

from generators.test_case_generator import TestCaseGenerator
from config import DIMESHIFT_NAME, SIMIDF_GENERATOR_NAME, TFIDF_GENERATOR_NAME

def test_generator_loading(generator_name, app_name):
    """测试生成器加载功能"""
    try:
        print(f"正在测试 {generator_name} 生成器...")
        
        # 尝试加载生成器
        generator = TestCaseGenerator.load_generator(
            generator_name=generator_name,
            app_name=app_name,
            num_candidates=5,
            q=2,
            diversity_strategy="sequence"
        )
        
        print(f"✓ {generator_name} 生成器加载成功")
        print(f"  生成器类型: {type(generator).__name__}")
        print(f"  应用名称: {generator.app_name}")
        print(f"  类变量名: {generator.class_variable_name}")
        
        return True
        
    except Exception as e:
        print(f"✗ {generator_name} 生成器加载失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试新的测试生成器...")
    print("=" * 50)
    
    app_name = DIMESHIFT_NAME
    
    # 测试SimIDF生成器
    simidf_success = test_generator_loading(SIMIDF_GENERATOR_NAME, app_name)
    print()
    
    # 测试TFIDF生成器
    tfidf_success = test_generator_loading(TFIDF_GENERATOR_NAME, app_name)
    print()
    
    print("=" * 50)
    if simidf_success and tfidf_success:
        print("✓ 所有生成器测试通过！")
    else:
        print("✗ 部分生成器测试失败")
        
    return simidf_success and tfidf_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)