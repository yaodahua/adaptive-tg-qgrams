#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'web-application-code'))

from config import DIMESHIFT_NAME, SIMIDF_GENERATOR_NAME, TFIDF_GENERATOR_NAME
from generators.test_case_generator import TestCaseGenerator

def test_generator_through_main(generator_name, app_name):
    """通过main.py的流程测试生成器"""
    try:
        print(f"正在测试 {generator_name} 通过main.py流程...")
        
        # 模拟main.py中的生成器加载逻辑
        generator = TestCaseGenerator.load_generator(
            generator_name=generator_name,
            app_name=app_name,
            num_candidates=3,
            diversity_strategy="sequence",
            q=2 if generator_name == TFIDF_GENERATOR_NAME else 0
        )
        
        print(f"✓ 生成器加载成功: {type(generator).__name__}")
        
        # 测试生成器是否能生成测试用例
        from executors.coverage_target import CoverageTarget
        import pickle
        from utils.file_utils import get_coverage_targets_file
        
        # 加载覆盖率目标
        coverage_targets_filepath = get_coverage_targets_file(app_name=app_name)
        with open(coverage_targets_filepath, "rb") as f:
            coverage_targets = pickle.load(f)
        
        # 使用前几个覆盖率目标进行测试
        test_coverage_targets = coverage_targets[:5] if len(coverage_targets) > 5 else coverage_targets
        
        print(f"✓ 覆盖率目标加载成功")
        
        # 生成测试用例
        individual = generator.generate(
            uncovered_targets=test_coverage_targets,
            max_length=10
        )
        
        # 获取测试用例字符串表示
        test_cases = individual.to_string()
        
        print(f"✓ 测试用例生成成功，生成了 {len(test_cases)} 条语句")
        
        # 验证测试用例格式
        assert len(test_cases) > 0, "未生成任何测试用例"
        for test_case in test_cases:
            assert isinstance(test_case, str), f"测试用例不是字符串: {type(test_case)}"
            assert len(test_case) > 0, "生成了空测试用例"
        
        print(f"✓ 测试用例格式验证通过")
        
        return True
        
    except Exception as e:
        print(f"✗ {generator_name} 通过main.py流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        
        return False

def main():
    print("开始最终集成测试...")
    print("=" * 60)
    
    app_name = DIMESHIFT_NAME
    
    # 测试SimIDF生成器
    simidf_success = test_generator_through_main(SIMIDF_GENERATOR_NAME, app_name)
    
    print()
    
    # 测试TFIDF生成器
    tfidf_success = test_generator_through_main(TFIDF_GENERATOR_NAME, app_name)
    
    print()
    print("=" * 60)
    
    if simidf_success and tfidf_success:
        print("✓ 所有最终集成测试通过！")
        print()
        print("新生成器已完全集成到系统中，可以通过以下命令使用：")
        print(f"  python main.py --app_name {app_name} --generator_name {SIMIDF_GENERATOR_NAME}")
        print(f"  python main.py --app_name {app_name} --generator_name {TFIDF_GENERATOR_NAME}")
        return 0
    else:
        print("✗ 最终集成测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())