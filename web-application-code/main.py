"""
自适应测试生成主程序模块
功能: 基于Q-gram的自适应随机测试生成系统, 支持多种测试生成策略和恢复执行
主要特性:
- 支持多种测试用例生成器(随机, 距离, Q-gram, TF-IDF, SimIDF)
- 支持从断点恢复执行
- 实时监控代码覆盖率
- 容器化测试环境管理
- 详细的执行统计和结果保存
"""

import json
import os
from pathlib import Path
import pickle
import re
import time
import docker
import numpy as np
import requests
from config import (
    APP_NAMES,
    CHROME_CONTAINER_NAME,
    DIMESHIFT_NAME,
    DISTANCE_GENERATOR_NAME,
    DIVERSITY_STRATEGY_NAMES,
    GENERATOR_NAMES,
    QGRAMS_GENERATOR_NAME,
    RANDOM_GENERATOR_NAME,
    SEQUENCE_DIVERSITY_STRATEGY_NAME,
    SIMIDF_GENERATOR_NAME,
    TFIDF_GENERATOR_NAME,
)
from executors.executor import Executor
from generators.test_case_generator import TestCaseGenerator
from global_log import GlobalLog
from individuals.individual import Individual
from parsing.instrument import Instrument
from utils.file_utils import get_coverage_targets_file
from utils.randomness_utils import RandomGenerator, set_random_seed
from tqdm import tqdm

import argparse

# 命令行参数解析器
args = argparse.ArgumentParser()
args.add_argument(
    "--app-name",  # 被测试应用名称
    help="Name of the app under test",
    type=str,
    choices=APP_NAMES,
    default=DIMESHIFT_NAME,
)
args.add_argument(
    "--generator-name",  # 测试用例生成器名称
    help="Name of the generator",
    type=str,
    choices=GENERATOR_NAMES,
    default=RANDOM_GENERATOR_NAME,
)
args.add_argument("--budget", help="Budget in seconds", type=int, default=180)  # 测试时间预算(秒)
args.add_argument(
    "--seed", help="Seed for random number generation", type=int, default=-1  # 随机数种子
)
args.add_argument("--progress", help="Activate progress bar", action="store_true")  # 显示进度条
args.add_argument(
    "--resume-filepath",  # 恢复执行文件路径
    help="Path to the json file containing the execution stats for resuming",
    type=str,
    default=None,
)
args.add_argument(
    "--max-length", help="Maximum length of the test case", type=int, default=30  # 测试用例最大长度
)
args.add_argument(
    "--num-candidates",  # 候选测试用例数量
    help=f"Number of candidates for generators {DISTANCE_GENERATOR_NAME}/ {QGRAMS_GENERATOR_NAME}/{SIMIDF_GENERATOR_NAME}/{TFIDF_GENERATOR_NAME}",
    type=int,
    default=5,
)
args.add_argument(
    "--q",  # Q-gram参数
    help=f"Number of qgrams for generator {QGRAMS_GENERATOR_NAME}",
    type=int,
    default=2,
)
args.add_argument(
    "--diversity-strategy",  # 多样性策略
    help=f"Number of candidates for generators {DISTANCE_GENERATOR_NAME} and {QGRAMS_GENERATOR_NAME}",
    type=str,
    choices=DIVERSITY_STRATEGY_NAMES,
    default=SEQUENCE_DIVERSITY_STRATEGY_NAME,
)
args, _ = args.parse_known_args()  # 解析命令行参数


if __name__ == "__main__":
    """主程序入口点"""
    
    logger = GlobalLog(logger_prefix="Main")  # 初始化日志记录器

    # 解析命令行参数
    app_name = args.app_name  # 被测试应用名称
    generator_name = args.generator_name  # 测试用例生成器名称
    budget = args.budget  # 测试时间预算(秒)
    max_length = args.max_length  # 测试用例最大长度
    num_candidates = args.num_candidates  # 候选测试用例数量
    q = args.q  # Q-gram参数
    progress = args.progress  # 是否显示进度条
    diversity_strategy = args.diversity_strategy  # 多样性策略
    resume_filepath = args.resume_filepath  # 恢复执行文件路径

    # 恢复执行逻辑
    if resume_filepath is not None:
        assert os.path.exists(resume_filepath), "Resume filepath does not exist"  # 验证恢复文件存在
        assert resume_filepath.endswith(
            ".json"
        ), "Resume filepath should be a json file"  # 验证文件格式为JSON

        prefix = resume_filepath.split(os.sep)[-1]  # 提取文件名
        parent_filepath = Path(resume_filepath).parent  # 获取父目录路径

        # 从文件名中提取种子和日期信息
        match_seed = re.search(r"(\d+).json", prefix)
        match_date = re.search(r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})", prefix)

        assert match_seed is not None, "Seed not found in the filename"  # 验证种子存在
        assert match_date is not None, "Date not found in the filename"  # 验证日期存在
        seed = int(match_seed.group(0).replace(".json", ""))  # 提取种子值
        previous_date = match_date.group(0)  # 提取日期值

        # 处理命令行种子与文件种子冲突
        if args.seed != -1:
            logger.info(
                f"Command line seed is {args.seed} is ignored in favor of the seed in the filename {seed}"
            )

        # 加载恢复执行数据
        with open(resume_filepath, "r") as f:
            data = json.load(f)  # 读取JSON数据
            exhausted_budget = data["exhausted_budget"]  # 获取预算耗尽状态
            assert not exhausted_budget, "Budget is exhausted, no need to resume"  # 验证预算未耗尽
            previous_time_elapsed = data["time_elapsed"]  # 获取已用时间

            # 验证参数一致性
            assert (
                data["app_name"] == app_name
            ), "App name is different from previous execution"  # 验证应用名称一致
            assert (
                data["budget"] == budget
            ), "Budget is different from previous execution"  # 验证预算一致

            budget -= previous_time_elapsed  # 计算剩余预算
            previous_iterations = data["iterations"]  # 获取已执行迭代次数
            assert (
                max_length == data["max_length"]
            ), "Max length is different from previous execution"  # 验证最大长度一致
            assert (
                data["generator"] == generator_name
            ), "Generator name is different from previous execution"  # 验证生成器一致
            
            # 验证特定生成器的参数一致性
            if (
                generator_name == DISTANCE_GENERATOR_NAME
                or generator_name == QGRAMS_GENERATOR_NAME
            ):
                assert (
                    data["num_candidates"] == num_candidates
                ), "Number of candidates is different from previous execution"  # 验证候选数量一致

                assert (
                    data["diversity_strategy"] == diversity_strategy
                ), "Diversity strategy is different from previous execution"  # 验证多样性策略一致

                if generator_name == QGRAMS_GENERATOR_NAME:
                    assert (
                        data["q"] == q
                    ), "Number of qgrams is different from previous execution"  # 验证Q-gram参数一致

            logger.info(
                f"Resuming execution for {app_name} from file {resume_filepath} "
                f"for the remainig budget of {budget} seconds"
            )  # 记录恢复执行信息

            # 获取历史执行数据
            previous_generation_times = data["generation_times"]  # 历史生成时间
            previous_execution_times = data["execution_times"]  # 历史执行时间
            previous_coverage_over_time = data["coverage_over_time"]  # 历史覆盖率数据
            previous_individual_lengths = data["individual_lengths"]  # 历史个体长度数据

        # 加载生成器状态(非随机生成器需要状态恢复)
        if generator_name != RANDOM_GENERATOR_NAME:
            with open(
                os.path.join(
                    parent_filepath, f"{previous_date}_{seed}_generator_state.pkl"
                ),
                "rb",
            ) as f:
                generator_state = pickle.load(f)  # 加载生成器状态
        else:
            generator_state = None  # 随机生成器无需状态恢复

        # 加载随机数状态
        with open(
            os.path.join(parent_filepath, f"{previous_date}_{seed}_random_state.pkl"),
            "rb",
        ) as f:
            random_state = pickle.load(f)  # 加载随机数状态

        # 加载已覆盖目标
        with open(
            os.path.join(
                parent_filepath, f"{previous_date}_{seed}_covered_targets.pkl"
            ),
            "rb",
        ) as f:
            covered_targets = pickle.load(f)  # 加载已覆盖目标列表

        # 加载最终测试套件
        with open(
            os.path.join(
                parent_filepath, f"{previous_date}_{seed}_final_test_suite.pkl"
            ),
            "rb",
        ) as f:
            final_test_suite = pickle.load(f)  # 加载最终测试套件

        set_random_seed(seed=seed, random_state=random_state)  # 设置随机数种子

    else:
        # 新执行逻辑(非恢复模式)
        seed = args.seed  # 获取命令行种子

        if seed == -1:
            # 随机生成种子
            try:
                # 在某些机器上, 2^32可能会溢出
                seed = np.random.randint(2**32 - 1, dtype="int64").item()
            except ValueError as _:
                seed = np.random.randint(2**30 - 1, dtype="int64").item()

        set_random_seed(seed=seed)  # 设置随机数种子

    # 验证生成器参数有效性
    if (
        generator_name == DISTANCE_GENERATOR_NAME
        or generator_name == QGRAMS_GENERATOR_NAME 
        or generator_name == SIMIDF_GENERATOR_NAME
        or generator_name == TFIDF_GENERATOR_NAME
    ):
        assert num_candidates > 0, "Number of candidates should be positive"  # 候选数量必须为正数
    if generator_name == QGRAMS_GENERATOR_NAME:
        assert q > 0, "Number of qgrams should be positive"  # Q-gram参数必须为正数

    executor = Executor.load_executor(app_name=app_name)  # 加载执行器
    try:
        network_name = executor.start_containers()  # 启动容器
    except RuntimeError as e:
        logger.error(f"Error starting containers: {e}")
        exit(1)  # 容器启动失败时退出程序

    coverage_targets_filepath = get_coverage_targets_file(app_name=app_name)  # 获取覆盖率目标文件路径

    if os.path.exists(coverage_targets_filepath):  # 如果覆盖率目标文件存在
        with open(coverage_targets_filepath, "rb") as f:
            coverage_targets = pickle.load(f)  # 从文件加载覆盖率目标
    else:  # 如果覆盖率目标文件不存在
        instrument_instance = Instrument(app_name=app_name)  # 创建插桩实例
        coverage_targets = instrument_instance.add_probes_and_get_coverage_targets()  # 添加探针并获取覆盖率目标

    # 初始化覆盖目标列表
    if resume_filepath is not None:  # 如果是恢复执行模式
        uncovered_targets = [
            ct.clone() for ct in coverage_targets if ct not in covered_targets  # 获取未覆盖目标
        ]
    else:  # 如果是新执行模式
        uncovered_targets = [ct.clone() for ct in coverage_targets]  # 所有目标都未覆盖
        covered_targets = []  # 已覆盖目标列表为空
    
    # 初始化进度条
    if progress:
        pbar = tqdm(total=len(coverage_targets), desc="Coverage Progress", unit="unit")
        if resume_filepath is not None:
            pbar.update(len(covered_targets))

    # 加载测试用例生成器
    generator = TestCaseGenerator.load_generator(
        diversity_strategy=diversity_strategy,
        generator_name=generator_name,
        num_candidates=num_candidates,
        app_name=app_name,
        q=q,
    )  # 根据参数加载对应的测试用例生成器

    if resume_filepath is not None and generator_state is not None:  # 恢复模式下设置生成器状态
        generator.set_state(generator_state=generator_state)  # 恢复生成器状态

    if resume_filepath is not None and final_test_suite is not None:  # 恢复模式下设置最终测试套件
        generator.set_final_test_suite(final_test_suite=final_test_suite)  # 恢复最终测试套件

    start_time = time.perf_counter()  # 记录开始时间
    result_json = {}  # 初始化结果JSON字典
    iterations = 0  # 迭代次数计数器
    coverage_over_time = []  # 覆盖率随时间变化列表
    generation_times = []  # 测试用例生成时间列表
    execution_times = []  # 测试用例执行时间列表
    individual_lengths = []  # 个体长度列表

    compile_instr = True  # 首次执行需要编译插桩代码

    chrome_container_name = None  # Chrome容器名称初始化为None

    try:

        while ( # 继续生成测试用例直到覆盖所有目标或超出预算
            len(covered_targets) < len(coverage_targets)
            and time.perf_counter() - start_time < budget
        ):

            try:
                _ = executor.get_container_name( 
                    network_name=network_name, container_type=CHROME_CONTAINER_NAME  # 获取Chrome容器名称
                )
            except RuntimeError:  # 如果Chrome容器不存在
                assert (
                    chrome_container_name is not None
                ), "Chrome container name is None"  # 确保Chrome容器名称不为空

                max_counter = 10  # 最大重试次数
                exception = True
                while exception and max_counter > 0:  # 重试启动容器
                    try:
                        executor.start_container_by_name(
                            network_name=network_name,
                            container_name=chrome_container_name,
                            add_container_to_network=True,
                        )  # 启动Chrome容器
                        exception = False
                    except (
                        docker.errors.NotFound,
                        requests.exceptions.ConnectionError,
                    ) as e:
                        logger.error(f"Error starting container: {e}")
                        max_counter -= 1
                        time.sleep(1)  # 等待1秒后重试
                assert (
                    max_counter > 0
                ), f"Max counter for starting container {chrome_container_name} reached"  # 确保容器启动成功

            start_time_generation = time.perf_counter()  # 记录生成开始时间
            individual = generator.generate(
                uncovered_targets=uncovered_targets, max_length=max_length
            )  # 生成测试用例个体
            end_time_generation = time.perf_counter()  # 记录生成结束时间
            individual_lengths.append(len(individual.statements))  # 记录个体长度

            max_counter = 10  # 最大重试次数
            exception = True
            excecution_output = None
            while exception and max_counter > 0:  # 重试执行测试用例

                try:
                    start_time_execution = time.perf_counter()  # 记录执行开始时间
                    execution_output = executor.execute(
                        individual=individual,
                        network_name=network_name,
                        compile_instr=compile_instr,
                    )  # 执行测试用例
                    exception = False
                except (
                    ValueError,
                    RuntimeError,
                    docker.errors.NotFound,
                    docker.errors.APIError,
                ) as err:
                    max_counter -= 1
                    time.sleep(1)  # 等待1秒后重试
                    logger.error(
                        f"Error during execution: {err}. "
                        f"All containers: {executor.list_all_containers()} "
                        f"All networks: {executor.list_all_networks()}"
                    )

            end_time_execution = time.perf_counter()  # 记录执行结束时间

            assert max_counter > 0, "Max counter for executing a test reached"  # 确保测试执行成功
            assert execution_output is not None, "Execution output is None"  # 确保执行输出不为空
            current_covered_targets = execution_output.get_covered_targets()  # 获取当前覆盖的目标

            for ct in current_covered_targets:  # 遍历当前覆盖的目标
                if ct in coverage_targets and ct not in covered_targets:  # 如果是新覆盖的目标且存在于目标列表中
                    ct_clone = ct.clone()  # 克隆目标对象
                    ct_clone.iteration = iterations  # 记录覆盖时的迭代次数
                    covered_targets.append(ct_clone)  # 添加到已覆盖目标列表
                    if progress:  # 如果启用了进度条
                        pbar.update(1)  # 更新进度条
                if ct in uncovered_targets:  # 如果目标在未覆盖列表中
                    uncovered_targets.remove(ct)  # 从未覆盖列表中移除

            if progress:  # 如果启用了进度条
                pbar.update(0)  # 刷新进度条显示

            logger.debug(f"Current covered targets: {len(current_covered_targets)}")  # 记录当前覆盖目标数量
            logger.debug(f"Global covered targets: {len(covered_targets)}")  # 记录全局已覆盖目标数量
            logger.debug(f"Global uncovered targets: {len(uncovered_targets)}")  # 记录全局未覆盖目标数量
            logger.debug(
                f"Global coverage: {100 * len(covered_targets) / len(coverage_targets):.2f}%"
            )  # 记录全局覆盖率
            logger.debug(f"Time elapsed: {time.perf_counter() - start_time:.2f}s")  # 记录已用时间
            logger.debug(
                f"Time generation: {end_time_generation - start_time_generation:.2f}s"
            )  # 记录生成时间
            logger.debug(
                f"Time execution: {end_time_execution - start_time_execution:.2f}s"
            )  # 记录执行时间
            coverage_over_time.append(
                100 * len(covered_targets) / len(coverage_targets)  # 记录当前覆盖率百分比
            )

            assert len(uncovered_targets) + len(covered_targets) == len(
                coverage_targets
            ), "Sum of covered and uncovered targets should be equal to the total number of targets"  # 验证覆盖目标数量一致性

            generation_times.append(end_time_generation - start_time_generation)  # 记录生成时间
            execution_times.append(end_time_execution - start_time_execution)  # 记录执行时间

            feasible_statements_strings = execution_output.get_feasible_prefix(
                app_name=app_name
            )  # 获取可行前缀
            feasible_individual = Individual.parse_statement_strings(
                statement_strings=feasible_statements_strings
            )  # 解析可行前缀为个体对象
            generator.update_final_test_suite(
                individual=feasible_individual, covered_targets=current_covered_targets
            )  # 更新最终测试套件

            # stopping the chrome container is needed to avoid a memory leak during the execution
            chrome_container_name = executor.get_container_name(
                network_name=network_name, container_type=CHROME_CONTAINER_NAME
            )  # 获取Chrome容器名称
            exception = True
            max_counter = 10
            while exception and max_counter > 0:  # 重试停止容器
                try:
                    executor.stop_container_by_name(
                        network_name=network_name,
                        container_name=chrome_container_name,
                        remove_container_from_network=True,
                    )  # 停止Chrome容器
                    exception = False
                except docker.errors.APIError as e:
                    logger.error(f"Error stopping container: {e}")
                    max_counter -= 1
                    time.sleep(1)  # 等待1秒后重试
            assert (
                max_counter > 0
            ), f"Max counter for stopping container {chrome_container_name} reached"  # 确保容器停止成功

            # compiling the instrumented class is only needed once
            compile_instr = False  # 后续执行无需重新编译插桩代码
            iterations += 1  # 迭代次数加1

    finally:  # 无论是否发生异常都会执行的清理代码
        executor.stop_containers(network_name=network_name)  # 停止所有容器
        if progress:  # 如果启用了进度条
            pbar.close()  # 关闭进度条

        time_elapsed = round(time.perf_counter() - start_time, 2)  # 计算总耗时
        date = time.strftime("%Y-%m-%d_%H-%M-%S")  # 获取当前日期时间
        exhausted_budget = time.perf_counter() - start_time > budget or len(
            covered_targets
        ) == len(coverage_targets)  # 判断预算是否耗尽或已覆盖所有目标
        if resume_filepath is not None:  # 如果是恢复执行模式
            date = previous_date  # 使用之前的日期
            time_elapsed += previous_time_elapsed  # 累加之前的时间
            iterations += previous_iterations  # 累加之前的迭代次数
            # reset budget to the original value
            budget = args.budget  # 重置预算为原始值
            generation_times = previous_generation_times + generation_times  # 合并生成时间
            execution_times = previous_execution_times + execution_times  # 合并执行时间
            coverage_over_time = previous_coverage_over_time + coverage_over_time  # 合并覆盖率数据
            individual_lengths = previous_individual_lengths + individual_lengths  # 合并个体长度数据

        result_json["seed"] = seed
        result_json["exhausted_budget"] = exhausted_budget
        result_json["time_elapsed"] = time_elapsed
        result_json["iterations"] = iterations
        result_json["max_length"] = max_length
        result_json["generator"] = generator_name
        if (
            generator_name == DISTANCE_GENERATOR_NAME
            or generator_name == QGRAMS_GENERATOR_NAME
        ):
            result_json["num_candidates"] = num_candidates
            result_json["diversity_strategy"] = diversity_strategy
            if generator_name == QGRAMS_GENERATOR_NAME:
                result_json["q"] = q
        result_json["app_name"] = app_name
        result_json["budget"] = budget
        result_json["num_covered_targets"] = len(covered_targets)
        result_json["num_uncovered_targets"] = len(uncovered_targets)
        result_json["global_coverage"] = round(
            100 * len(covered_targets) / len(coverage_targets), 3
        )
        result_json["avg_generation_time"] = np.mean(generation_times)
        result_json["avg_execution_time"] = np.mean(execution_times)
        result_json["avg_individual_length"] = np.mean(individual_lengths)
        result_json["generation_times"] = generation_times
        result_json["execution_times"] = execution_times
        result_json["coverage_over_time"] = coverage_over_time
        result_json["individual_lengths"] = individual_lengths

        json_string = json.dumps(result_json, indent=4)

        if (
            generator_name == DISTANCE_GENERATOR_NAME
            or generator_name == QGRAMS_GENERATOR_NAME
            or generator_name == SIMIDF_GENERATOR_NAME
            or generator_name == TFIDF_GENERATOR_NAME
        ):
            results_dir = os.path.join(
                os.getcwd(),
                "results",
                app_name,
                generator_name + "_" + diversity_strategy,
            )
        else:
            results_dir = os.path.join(os.getcwd(), "results", app_name, generator_name)

        os.makedirs(results_dir, exist_ok=True)
        result_filename = os.path.join(results_dir, f"{date}_{seed}.json")

        with open(
            os.path.join(results_dir, result_filename), "w+", encoding="utf-8"
        ) as f:
            f.write(json_string)

        test_suite_filename = os.path.join(results_dir, f"{date}_{seed}_test_suite.txt")
        with open(test_suite_filename, "w+", encoding="utf-8") as f:
            f.write(generator.write_final_test_suite(covered_targets=covered_targets))

        covered_targets_filename = os.path.join(
            results_dir, f"{date}_{seed}_covered_targets.pkl"
        )
        with open(covered_targets_filename, "wb") as f:
            pickle.dump(covered_targets, f)

        generator_state = generator.get_state()
        if generator_state is not None:
            generator_state_filename = os.path.join(
                results_dir, f"{date}_{seed}_generator_state.pkl"
            )
            with open(generator_state_filename, "wb") as f:
                pickle.dump(generator_state, f)

        random_state = RandomGenerator.get_instance().rnd_state.get_state()
        random_state_filename = os.path.join(
            results_dir, f"{date}_{seed}_random_state.pkl"
        )
        with open(random_state_filename, "wb") as f:
            pickle.dump(random_state, f)

        final_test_suite = generator.get_final_test_suite()
        final_test_suite_filename = os.path.join(
            results_dir, f"{date}_{seed}_final_test_suite.pkl"
        )
        with open(final_test_suite_filename, "wb") as f:
            pickle.dump(final_test_suite, f)
