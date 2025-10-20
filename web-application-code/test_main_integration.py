#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'web-application-code'))

from config import DIMESHIFT_NAME, SIMIDF_GENERATOR_NAME, TFIDF_GENERATOR_NAME, GENERATOR_NAMES
import argparse

def test_main_with_generator(generator_name, app_name):
    """测试main.py与特定生成器的集成"""
    try:
        print(f"正在测试 {generator_name} 与main.py的集成...")
        
        # 测试生成器名称是否在GENERATOR_NAMES中
        assert generator_name in GENERATOR_NAMES, f"生成器名称 {generator_name} 不在GENERATOR_NAMES中"
        
        print(f"✓ 生成器名称 {generator_name} 在GENERATOR_NAMES中")
        
        # 测试参数解析
        import main  # 导入main模块来访问全局变量
        
        # 检查main模块中的GENERATOR_NAMES是否包含新生成器
        assert generator_name in main.GENERATOR_NAMES, f"生成器名称 {generator_name} 不在main.GENERATOR_NAMES中"
        
        print(f"✓ 生成器名称 {generator_name} 在main.GENERATOR_NAMES中")
        
        # 测试参数解析器是否能接受新生成器
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--generator-name",
            help="Name of the generator",
            type=str,
            choices=main.GENERATOR_NAMES,
            default=main.RANDOM_GENERATOR_NAME,
        )
        
        # 测试解析特定生成器名称
        test_args = ['--generator-name', generator_name]
        args = parser.parse_args(test_args)
        
        assert args.generator_name == generator_name, f"参数解析失败: {args.generator_name} != {generator_name}"
        
        print(f"✓ 参数解析成功")
        print(f"  生成器名称: {args.generator_name}")
        
        return True
        
    except Exception as e:
        print(f"✗ {generator_name} 与main.py集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        
        return False

def main():
    """主测试函数"""
    print("开始测试main.py集成...")
    print("=" * 60)
    
    app_name = DIMESHIFT_NAME
    
    # 测试SimIDF生成器与main.py的集成
    simidf_success = test_main_with_generator(SIMIDF_GENERATOR_NAME, app_name)
    print()
    
    # 测试TFIDF生成器与main.py的集成
    tfidf_success = test_main_with_generator(TFIDF_GENERATOR_NAME, app_name)
    print()
    
    print("=" * 60)
    if simidf_success and tfidf_success:
        print("✓ 所有main.py集成测试通过！")
        print("\n新生成器已成功集成到系统中，可以通过以下命令使用：")
        print(f"  python main.py --app_name {app_name} --generator_name {SIMIDF_GENERATOR_NAME}")
        print(f"  python main.py --app_name {app_name} --generator_name {TFIDF_GENERATOR_NAME}")
    else:
        print("✗ 部分main.py集成测试失败")
        
    return simidf_success and tfidf_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)