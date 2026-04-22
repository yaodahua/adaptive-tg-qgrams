"""
基于JS散度的自适应随机测试(ART)生成器

本文件实现了基于Jensen-Shannon散度的自适应随机测试生成器.
主要特点:
1. 使用JS散度衡量测试用例与已有测试套件的多样性
2. 支持两种多样性策略: 序列多样性和输入多样性
3. 增量更新全局q-gram频率分布
4. 从候选测试用例中选择JS散度最大的个体

JS散度优势: 对称性, 有界性(0-1), 对分布差异更敏感
"""

import math
from collections import defaultdict
from functools import reduce
from pathlib import Path
import pickle
import time
import numpy as np
from typing import Dict, List, Optional, Tuple
from config import (
    DIMESHIFT_NAME,
    DIVERSITY_STRATEGY_NAMES,
    INPUT_DIVERSITY_STRATEGY_NAME,
    SEQUENCE_DIVERSITY_STRATEGY_NAME,
)
from executors.coverage_target import CoverageTarget
from generators.test_case_generator import TestCaseGenerator
from global_log import GlobalLog
from individuals.individual import Individual
from statements.class_declaration_statement import ClassDeclarationStatement
from statements.enum_statement import EnumStatement
from statements.method_call_statement import MethodCallStatement
from statements.variable_declaration import VariableDeclaration
from type_aliases import GeneratorState
from utils.file_utils import (
    get_class_under_test_path,
    get_coverage_targets_file,
)
from utils.randomness_utils import set_random_seed


def compute_js_divergence(global_dict, candidate_dict, global_total=None, candidate_total=None):
    """
    计算候选字典与全局字典的JS散度
    
    优化: 直接在循环中计算,避免中间字典的创建
    减少字典查找和重复计算,提高性能
    
    Args:
        global_dict: 全局q-gram频率字典
        candidate_dict: 候选q-gram频率字典
        global_total: 全局字典总和(可选,避免重复计算)
        candidate_total: 候选字典总和(可选,避免重复计算)
    
    Returns:
        JS散度值
    """
    # 计算总频率(如果未提供参数)
    if global_total is None:
        global_total = sum(global_dict.values())
    if candidate_total is None:
        candidate_total = sum(candidate_dict.values())
    
    # 如果任一字典为空,返回0
    if global_total == 0 or candidate_total == 0:
        return 0.0
    
    # 如果全局分布为空但候选分布不为空,返回一个较大的值以鼓励选择
    if global_total == 0 and candidate_total > 0:
        return 1.0
    
    # 优化: 避免重复计算倒数
    inv_global_total = 1.0 / global_total
    inv_candidate_total = 1.0 / candidate_total
    
    # 优化: 使用更高效的集合合并策略
    # 优先遍历较小的字典以减少迭代次数
    if len(global_dict) < len(candidate_dict):
        smaller_dict, larger_dict = global_dict, candidate_dict
    else:
        smaller_dict, larger_dict = candidate_dict, global_dict
    
    # 平滑参数
    epsilon = 1e-10
    
    # 计算JS散度
    js_div = 0.0
    
    # 优化: 减少字典查找次数
    # 首先处理较小字典中的gram
    for gram in smaller_dict:
        g_count = global_dict.get(gram, 0)
        c_count = candidate_dict.get(gram, 0)
        
        # 计算概率
        p = g_count * inv_global_total
        q = c_count * inv_candidate_total
        m = (p + q) * 0.5
        
        # 计算KL散度 KL(P||M)
        if p > epsilon and m > epsilon:
            js_div += p * math.log(p / m)
        
        # 计算KL散度 KL(Q||M)
        if q > epsilon and m > epsilon:
            js_div += q * math.log(q / m)
    
    # 然后处理较大字典中独有的gram
    for gram in larger_dict:
        if gram not in smaller_dict:
            g_count = global_dict.get(gram, 0)
            c_count = candidate_dict.get(gram, 0)
            
            # 计算概率
            p = g_count * inv_global_total
            q = c_count * inv_candidate_total
            m = (p + q) * 0.5
            
            # 计算KL散度 KL(P||M)
            if p > epsilon and m > epsilon:
                js_div += p * math.log(p / m)
            
            # 计算KL散度 KL(Q||M)
            if q > epsilon and m > epsilon:
                js_div += q * math.log(q / m)
    
    js_div *= 0.5
    
    return js_div


class IncrementalJS:
    """
    增量JS散度计算类
    维护全局q-gram频率分布,用于与候选测试用例比较
    """
    
    def __init__(self):
        self.global_dict = defaultdict(int)  # 优化: 使用defaultdict避免键检查
        self.total_count = 0   # 总频率计数
    
    def update(self, new_dict):
        """
        更新全局频率字典
        
        优化: 使用defaultdict直接累加,避免键存在性检查
        
        Args:
            new_dict: 新的q-gram频率字典
        """
        # 优化: 直接累加,无需检查键是否存在
        for gram, count in new_dict.items():
            self.global_dict[gram] += count
        
        # 优化: 避免重复计算总和
        self.total_count += sum(new_dict.values())
    
    def compute_js(self, candidate_dict):
        """
        计算候选字典与全局字典的JS散度
        
        优化: 使用预计算的总和,避免重复计算
        
        Args:
            candidate_dict: 候选q-gram频率字典
        
        Returns:
            JS散度值
        """
        # 优化: 使用预计算的全局总和,避免重复计算
        candidate_total = sum(candidate_dict.values())
        return compute_js_divergence(
            self.global_dict, 
            candidate_dict, 
            global_total=self.total_count,  # 使用预计算的全局总和
            candidate_total=candidate_total
        )
    
    def reset(self):
        """
        重置状态
        """
        self.global_dict = {}
        self.total_count = 0


class JSARTTestCaseGenerator(TestCaseGenerator):
    """基于JS散度的自适应随机测试生成器"""

    def __init__(
        self,
        app_name: str,
        class_variable_name: str,
        num_candidates: int = 5,
        q: int = 2,
        diversity_strategy: str = SEQUENCE_DIVERSITY_STRATEGY_NAME,
    ):
        """
        初始化JSART测试用例生成器
        
        Args:
            app_name: 应用程序名称
            class_variable_name: 类变量名称
            num_candidates: 候选测试用例数量
            q: q-gram的q值
            diversity_strategy: 多样性策略
        """
        super().__init__(app_name=app_name, class_variable_name=class_variable_name)
        self.logger = GlobalLog(logger_prefix="JSARTTestCaseGenerator")
        self.num_candidates = num_candidates
        self.diversity_strategy = diversity_strategy
        self.q = q
        
        # 使用增量JS散度计算器
        self.js_calculator = IncrementalJS()
        
        assert (
            diversity_strategy in DIVERSITY_STRATEGY_NAMES
        ), "Invalid diversity strategy"

    def compute_qgrams(
        self, individual: Individual
    ) -> Dict[Tuple[str], int]:
        """
        计算个体的q-gram频率分布
        
        Args:
            individual: 测试用例个体
            
        Returns:
            q-gram频率字典
        """
        if self.diversity_strategy == SEQUENCE_DIVERSITY_STRATEGY_NAME:
            method_strs = list(
                map(
                    lambda x: x.method_name,
                    filter(
                        lambda x: isinstance(x, MethodCallStatement),
                        individual.statements,
                    ),
                )
            )
        elif self.diversity_strategy == INPUT_DIVERSITY_STRATEGY_NAME:
            methods = list(
                filter(
                    lambda x: isinstance(x, MethodCallStatement), individual.statements
                )
            )
            method_strs = []
            for method in methods:
                args = []
                for argument in method.arguments:
                    variable_name = argument.get_variable_name()
                    variable_declarations = list(
                        filter(
                            lambda x: isinstance(x, VariableDeclaration)
                            and x.get_variable_name() == variable_name,
                            individual.statements,
                        )
                    )
                    assert (
                        len(variable_declarations) == 1
                    ), "There should be only one variable"
                    variable_declaration = variable_declarations[0]
                    if isinstance(variable_declaration, ClassDeclarationStatement):
                        if variable_declaration.value is None:
                            args.append(f"{variable_declaration.class_name}()")
                        else:
                            args.append(
                                f"{variable_declaration.class_name}({variable_declaration.value})"
                            )
                    elif isinstance(variable_declaration, EnumStatement):
                        args.append(
                            f"{variable_declaration.class_name}.{variable_declaration.value}"
                        )
                    else:
                        raise RuntimeError(
                            f"Unknown variable declaration: {variable_declaration}"
                        )
                method_strs.append(f"{method.method_name}({', '.join(args)})")
        else:
            raise RuntimeError(f"Unknown diversity strategy: {self.diversity_strategy}")

        qgram_counts = defaultdict(int)

        for i in range(len(method_strs) - self.q + 1):
            qgram = tuple(method_strs[i : i + self.q])
            qgram_counts[qgram] += 1

        return dict(qgram_counts)

    def generate(
        self, uncovered_targets: List[CoverageTarget], max_length: int = 30
    ) -> Individual:
        """
        生成测试用例
        
        Args:
            uncovered_targets: 未覆盖的目标列表
            max_length: 测试用例最大长度
            
        Returns:
            生成的测试用例
        """
        uncovered_edge_names = reduce(
            lambda acc, item: acc + [item] if item not in acc else acc,
            map(lambda x: x.method_name, uncovered_targets),
            [],
        )

        assert len(uncovered_edge_names) > 0, "Uncovered edge names should not be empty"

        target_edge_name = self.random_generator.rnd_state.choice(uncovered_edge_names)

        candidates = [
            self.generate_individual(
                target_edge_name=target_edge_name, max_length=max_length
            )
            for _ in range(self.num_candidates)
        ]

        selected_individual = None

        js_divergences = []
        individual_lengths = []
        
        for c in candidates:
            candidate_qgrams = self.compute_qgrams(individual=c)
            js_div = self.js_calculator.compute_js(candidate_qgrams)
            js_divergences.append(js_div)
            individual_lengths.append(len(c.statements))

        # 处理第一次运行时的特殊情况
        if len(js_divergences) == 0 or np.isnan(js_divergences).all():
            # 如果所有JS散度都是NaN（第一次运行），选择长度最长的候选
            index_max_js = np.argmax(individual_lengths)
        else:
            # 将NaN值替换为最小值，避免argmax错误
            js_divergences = np.nan_to_num(js_divergences, nan=-np.inf)
            
            # 平衡的JS散度与长度结合：标准化权重法
            # 1. 计算长度权重（对数增长，避免过度敏感）
            length_weights = np.log1p(individual_lengths)
            
            # 2. 结合JS散度和长度权重（70% JS散度，30%长度）
            js_weight = 0.7
            length_weight = 0.3
            
            # 3. 标准化JS散度到0-1范围（如果不在该范围）
            normalized_js = js_divergences / np.max(js_divergences) if np.max(js_divergences) > 0 else js_divergences
            
            # 4. 标准化长度权重到0-1范围
            normalized_lengths = length_weights / np.max(length_weights)
            
            # combined_scores = normalized_js* normalized_lengths #直接相乘
            # 加权和：保持JS散度主导，适度考虑长度
            combined_scores = js_weight * normalized_js + length_weight * normalized_lengths
            
            # 选择综合得分最高的候选测试用例
            index_max_js = np.argmax(combined_scores)
        
        selected_individual = candidates[index_max_js]

        assert selected_individual is not None, "Selected individual should not be None"

        # 更新全局状态
        self.store_executed_individual(individual=selected_individual)
        selected_qgrams = self.compute_qgrams(individual=selected_individual)
        self.js_calculator.update(selected_qgrams)

        return selected_individual

    def generate_new(
        self, uncovered_targets: List[CoverageTarget], max_length: int = 30
    ) -> Tuple[Individual, float]:
        """
        生成测试用例并返回计算时间
        
        Args:
            uncovered_targets: 未覆盖的目标列表
            max_length: 测试用例最大长度
            
        Returns:
            (生成的测试用例, JS散度计算时间)
        """
        uncovered_edge_names = reduce(
            lambda acc, item: acc + [item] if item not in acc else acc,
            map(lambda x: x.method_name, uncovered_targets),
            [],
        )

        assert len(uncovered_edge_names) > 0, "Uncovered edge names should not be empty"

        target_edge_name = self.random_generator.rnd_state.choice(uncovered_edge_names)

        candidates = [
            self.generate_individual(
                target_edge_name=target_edge_name, max_length=max_length
            )
            for _ in range(self.num_candidates)
        ]

        selected_individual = None
        start_time = time.perf_counter()

        js_divergences = []
        individual_lengths = []
        
        for c in candidates:
            candidate_qgrams = self.compute_qgrams(individual=c)
            js_div = self.js_calculator.compute_js(candidate_qgrams)
            js_divergences.append(js_div)
            individual_lengths.append(len(c.statements))

        # 处理第一次运行时的特殊情况
        if len(js_divergences) == 0 or np.isnan(js_divergences).all():
            # 如果所有JS散度都是NaN（第一次运行），选择长度最长的候选
            index_max_js = np.argmax(individual_lengths)
        else:
            # 将NaN值替换为最小值，避免argmax错误
            js_divergences = np.nan_to_num(js_divergences, nan=-np.inf)
            
            # 平衡的JS散度与长度结合：标准化权重法
            # 1. 计算长度权重（对数增长，避免过度敏感）
            length_weights = np.log1p(individual_lengths)
            
            # 2. 结合JS散度和长度权重（70% JS散度，30%长度）
            js_weight = 0.7
            length_weight = 0.3
            
            # 3. 标准化JS散度到0-1范围（如果不在该范围）
            normalized_js = js_divergences / np.max(js_divergences) if np.max(js_divergences) > 0 else js_divergences
            
            # 4. 标准化长度权重到0-1范围
            normalized_lengths = length_weights / np.max(length_weights)

            # combined_scores = normalized_js* normalized_lengths #直接相乘
            # 加权和：保持JS散度主导，适度考虑长度
            combined_scores = js_weight * normalized_js + length_weight * normalized_lengths
            
            # 选择综合得分最高的候选测试用例
            index_max_js = np.argmax(combined_scores)
        
        selected_individual = candidates[index_max_js]

        assert selected_individual is not None, "Selected individual should not be None"

        # 更新全局状态
        self.store_executed_individual(individual=selected_individual)
        selected_qgrams = self.compute_qgrams(individual=selected_individual)
        self.js_calculator.update(selected_qgrams)

        end_time = time.perf_counter()
        js_computation_time = end_time - start_time

        return selected_individual, js_computation_time

    def get_state(self) -> Optional[GeneratorState]:
        """获取生成器状态"""
        return {
            'global_dict': dict(self.js_calculator.global_dict),
            'total_count': self.js_calculator.total_count
        }

    def set_state(self, generator_state: GeneratorState) -> None:
        """设置生成器状态"""
        if generator_state is not None:
            self.js_calculator.global_dict = defaultdict(int, generator_state.get('global_dict', {}))
            self.js_calculator.total_count = generator_state.get('total_count', 0)


if __name__ == "__main__":
    set_random_seed(seed=0)

    app_name = DIMESHIFT_NAME
    diversity_strategy = SEQUENCE_DIVERSITY_STRATEGY_NAME

    coverage_targets_filepath = get_coverage_targets_file(app_name=app_name)

    with open(coverage_targets_filepath, "rb") as f:
        coverage_targets = pickle.load(f)

    class_filename = Path(
        get_class_under_test_path(app_name=app_name, is_instrumented=True)
    ).name
    class_filename_without_extension = class_filename.replace(".java", "")

    generator = JSARTTestCaseGenerator(
        app_name=app_name,
        class_variable_name=class_filename_without_extension,
        num_candidates=30,
        diversity_strategy=diversity_strategy,
        q=2,
    )

    individual_lengths = []
    js_computation_times = []
    for i in range(4000):
        start_time = time.perf_counter()
        individual, js_computation_time = generator.generate_new(
            uncovered_targets=coverage_targets, max_length=40
        )
        js_computation_times.append(js_computation_time)
        print(
            f"{i} Time to generate individual: {time.perf_counter() - start_time:2f}s"
        )
        individual_lengths.append(len(individual.statements))

    print(
        np.mean(js_computation_times),
        np.median(js_computation_times),
        np.max(js_computation_times),
    )

    print(f"Average individual lengths: {np.mean(individual_lengths)}")