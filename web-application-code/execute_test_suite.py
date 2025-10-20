"""
测试套件执行模块
功能: 执行预先生成的测试套件, 计算代码覆盖率, 并跟踪覆盖目标
"""

import os
import pickle

from tqdm import tqdm
from config import APP_NAMES, CHROME_CONTAINER_NAME, DIMESHIFT_NAME
from executors.executor import Executor
from generators.test_case_generator import TestCaseGenerator
from global_log import GlobalLog
from parsing.instrument import Instrument
from utils.file_utils import get_coverage_targets_file

import argparse

# 命令行参数解析
args = argparse.ArgumentParser()
args.add_argument(
    "--app-name",
    help="Name of the app under test",  # 被测试应用名称
    type=str,
    choices=APP_NAMES,
    default=DIMESHIFT_NAME,
)
args.add_argument(
    "--test-suite-filepath", help="Test suite file", type=str, default=None  # 测试套件文件路径
)
args, _ = args.parse_known_args()


if __name__ == "__main__":

    # 初始化日志记录器
    logger = GlobalLog(logger_prefix="execute_test_suite")

    # 获取命令行参数
    app_name = args.app_name
    test_suite_filepath = args.test_suite_filepath

    # 验证测试套件文件存在
    assert os.path.exists(
        test_suite_filepath
    ), f"Test suite file {test_suite_filepath} does not exist"

    # 验证应用名称与测试套件文件路径匹配
    assert (
        app_name in test_suite_filepath
    ), f"App name {app_name} is not in the test suite file path"

    # 加载执行器并启动容器
    executor = Executor.load_executor(app_name=app_name)
    network_name = executor.start_containers()

    # 获取覆盖率目标文件路径
    coverage_targets_filepath = get_coverage_targets_file(app_name=app_name)

    # 如果覆盖率目标文件存在, 则直接加载, 否则进行插桩
    if os.path.exists(coverage_targets_filepath):
        with open(coverage_targets_filepath, "rb") as f:
            coverage_targets = pickle.load(f)
        compile_instr = False  # 不需要重新编译插桩代码
    else:
        # 创建插桩实例并获取覆盖率目标
        instrument_instance = Instrument(app_name=app_name)
        coverage_targets = instrument_instance.add_probes_and_get_coverage_targets()
        compile_instr = True  # 需要编译插桩代码

    # 初始化覆盖目标跟踪
    uncovered_targets = [ct.clone() for ct in coverage_targets]  # 未覆盖目标列表
    covered_targets = []  # 已覆盖目标列表

    chrome_container_name = None  # Chrome容器名称

    # 解析测试套件
    test_suite = TestCaseGenerator.parse_final_test_suite(
        test_suite_filepath=test_suite_filepath
    )

    # 创建进度条
    pbar = tqdm(total=len(test_suite), desc="Number of Tests Progress", unit="unit")

    try:

        # 遍历测试套件中的每个测试用例
        for individual in test_suite:

            # 检查Chrome容器是否运行, 如果未运行则启动
            try:
                _ = executor.get_container_name(
                    network_name=network_name, container_type=CHROME_CONTAINER_NAME
                )
            except RuntimeError:
                assert (
                    chrome_container_name is not None
                ), "Chrome container name is None"
                executor.start_container_by_name(
                    network_name=network_name,
                    container_name=chrome_container_name,
                    add_container_to_network=True,
                )

            # 执行测试用例
            execution_output = executor.execute(
                individual=individual,
                network_name=network_name,
                compile_instr=compile_instr,
            )

            # 停止Chrome容器以避免内存泄漏
            chrome_container_name = executor.get_container_name(
                network_name=network_name, container_type=CHROME_CONTAINER_NAME
            )
            executor.stop_container_by_name(
                network_name=network_name,
                container_name=chrome_container_name,
                remove_container_from_network=True,
            )

            # 获取当前测试用例覆盖的目标
            current_covered_targets = execution_output.get_covered_targets()

            pbar.update(1)  # 更新进度条

            # 更新覆盖目标统计
            for ct in current_covered_targets:
                if ct in coverage_targets and ct not in covered_targets:
                    ct_clone = ct.clone()
                    covered_targets.append(ct_clone)  # 添加到已覆盖列表
                if ct in uncovered_targets:
                    uncovered_targets.remove(ct)  # 从未覆盖列表中移除

            # 记录调试信息
            logger.debug(f"Current covered targets: {len(current_covered_targets)}")
            logger.debug(f"Global covered targets: {len(covered_targets)}")
            logger.debug(f"Global uncovered targets: {len(uncovered_targets)}")
            logger.debug(
                f"Global coverage: {100 * len(covered_targets) / len(coverage_targets):.2f}%"
            )

            # 验证覆盖目标统计的正确性
            assert len(uncovered_targets) + len(covered_targets) == len(
                coverage_targets
            ), "Sum of covered and uncovered targets should be equal to the total number of targets"

    finally:
        pbar.close()
        executor.stop_containers(network_name=network_name)
