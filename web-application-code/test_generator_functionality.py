#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'web-application-code'))

from generators.test_case_generator import TestCaseGenerator
from config import DIMESHIFT_NAME, SIMIDF_GENERATOR_NAME, TFIDF_GENERATOR_NAME
import pickle
from utils.file_utils import get_coverage_targets_file

def test_generator_functionality(generator_name, app_name):
    """测试生成器功能"""
    try:
        print(f"正在测试 {generator_name} 生成器功能...")
        
        # 加载覆盖率目标
        coverage_targets_filepath = get_coverage_targets_file(app_name=app_name)
        with open(coverage_targets_filepath, "rb") as f:
            coverage_targets = pickle.load(f)
        
        # 加载生成器
        generator = TestCaseGenerator.load_generator(
            generator_name=generator_name,
            app_name=app_name,
            num_candidates=3,
            q=2,
            diversity_strategy="sequence"
        )
        
        print(f"✓ {generator_name} 生成器加载成功")
        
        # 测试生成测试用例
        print("  正在生成测试用例...")
        individual = generator.generate(
            uncovered_targets=coverage_targets[:10],  # 只使用前10个目标
            max_length=10
        )
        
        print(f"✓ 测试用例生成成功")
        print(f"  测试用例长度: {len(individual.statements)} 条语句")
        print(f"  测试用例内容预览:")
        
        # 显示前几条语句
        for i, statement in enumerate(individual.statements[:5]):
            print(f"    {i+1}. {statement}")
        
        if len(individual.statements) > 5:
            print(f"    ... 还有 {len(individual.statements) - 5} 条语句")
        
        # 测试状态管理
        print("  正在测试状态管理...")
        state = generator.get_state()
        print(f"✓ 状态获取成功: {state is not None}")
        
        if state is not None:
            generator.set_state(state)
            print(f"✓ 状态设置成功")
        
        return True
        
    except Exception as e:
        print(f"✗ {generator_name} 生成器功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试生成器功能...")
    print("=" * 60)
    
    app_name = DIMESHIFT_NAME
    
    # 测试SimIDF生成器
    simidf_success = test_generator_functionality(SIMIDF_GENERATOR_NAME, app_name)
    print()
    
    # 测试TFIDF生成器
    tfidf_success = test_generator_functionality(TFIDF_GENERATOR_NAME, app_name)
    print()
    
    print("=" * 60)
    if simidf_success and tfidf_success:
        print("✓ 所有生成器功能测试通过！")
    else:
        print("✗ 部分生成器功能测试失败")
        
    return simidf_success and tfidf_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)