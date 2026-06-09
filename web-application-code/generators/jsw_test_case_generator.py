"""
基于加权JS散度(Weighted Jensen-Shannon Divergence)的自适应随机测试生成器

主要特点:
1. 使用加权JS散度衡量测试用例与已有测试套件的多样性
2. 权重k由候选用例长度与已选集平均长度的比例动态决定
   k = L_P / (L_P + avg_L_Q)
3. 加权JS散度公式: JS_k(P || Q) = k * KL(P || M_k) + (1-k) * KL(Q || M_k)
   其中 M_k = k * P + (1-k) * Q
4. 支持两种多样性策略: 序列多样性和输入多样性
"""

import math
import sys
import os
from collections import defaultdict
from functools import reduce
from pathlib import Path
import pickle
import time
import numpy as np
from typing import Dict, List, Optional, Tuple

# 确保项目根目录在 sys.path 中，支持直接运行
_script_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_script_dir)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

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


def compute_weighted_js_divergence(
    global_dict, candidate_dict,
    global_total, candidate_total,
    k
):
    """
    计算加权JS散度: JS_k(P || Q) = k * KL(P || M_k) + (1-k) * KL(Q || M_k)
    其中 M_k = k * P + (1-k) * Q

    Args:
        global_dict: 全局q-gram频率字典(Q分布)
        candidate_dict: 候选q-gram频率字典(P分布)
        global_total: 全局字典总和
        candidate_total: 候选字典总和
        k: 权重系数, 取值范围[0, 1]

    Returns:
        加权JS散度值
    """
    if global_total == 0 or candidate_total == 0:
        return 0.0

    inv_global_total = 1.0 / global_total
    inv_candidate_total = 1.0 / candidate_total

    # 优先遍历较小的字典以减少迭代次数
    # if len(global_dict) < len(candidate_dict):
    #     smaller_dict, larger_dict = global_dict, candidate_dict
    # else:
    #     smaller_dict, larger_dict = candidate_dict, global_dict

    epsilon = 1e-10
    js_k = 0.0

    # 处理较小字典中的gram
    for gram in candidate_dict:
        g_count = global_dict.get(gram, 0)
        c_count = candidate_dict.get(gram, 0)

        p = c_count * inv_candidate_total   # P: 候选分布
        q = g_count * inv_global_total      # Q: 全局分布
        m_k = k * p + (1.0 - k) * q         # M_k = k*P + (1-k)*Q

        # k * KL(P || M_k)
        if p > epsilon and m_k > epsilon:
            js_k += k * p * math.log(p / m_k)

        # (1-k) * KL(Q || M_k)
        if q > epsilon and m_k > epsilon:
            js_k += (1.0 - k) * q * math.log(q / m_k)

    # 处理较大字典中独有的gram
    for gram in global_dict:
        if gram not in candidate_dict:
            g_count = global_dict.get(gram, 0)
            c_count = candidate_dict.get(gram, 0)

            p = c_count * inv_candidate_total
            q = g_count * inv_global_total
            m_k = k * p + (1.0 - k) * q

            if p > epsilon and m_k > epsilon:
                js_k += k * p * math.log(p / m_k)

            if q > epsilon and m_k > epsilon:
                js_k += (1.0 - k) * q * math.log(q / m_k)

    return js_k


class IncrementalJSW:
    """
    增量加权JS散度计算类
    维护全局q-gram频率分布和已选测试用例长度列表
    """

    def __init__(self):
        self.global_dict = defaultdict(int)
        self.total_count = 0
        self.lengths = []  # 已选测试用例的方法调用语句数列表, 用于计算avg_L_Q
        self.total_lengths = []  # 已选测试用例的总语句数列表

    def update(self, new_dict, length, total_length):
        """
        更新全局频率字典和长度列表

        Args:
            new_dict: 新的q-gram频率字典
            length: 被选中测试用例的方法调用语句数量
            total_length: 被选中测试用例的总语句数量
        """
        for gram, count in new_dict.items():
            self.global_dict[gram] += count
        self.total_count += sum(new_dict.values())
        self.lengths.append(length)
        self.total_lengths.append(total_length)

    def compute_weighted_js(self, candidate_dict, candidate_length):
        """
        计算候选字典与全局字典的加权JS散度

        Args:
            candidate_dict: 候选q-gram频率字典
            candidate_length: 候选测试用例的长度

        Returns:
            加权JS散度值
        """
        candidate_total = sum(candidate_dict.values())

        # 如果全局为空, 返回一个较大值以鼓励选择
        if self.total_count == 0 and candidate_total > 0:
            return 1.0

        # 计算k = L_P / (L_P + avg_L_Q)
        if len(self.lengths) == 0:
            avg_l_q = 0.0
        else:
            avg_l_q = sum(self.lengths) / len(self.lengths)

        if candidate_length + avg_l_q == 0:
            return 0.0

        k = candidate_length / (candidate_length + avg_l_q)
        
        # k = 0.5 #0.5的时候为纯js

        return compute_weighted_js_divergence(
            self.global_dict,
            candidate_dict,
            global_total=self.total_count,
            candidate_total=candidate_total,
            k=k,
        )

    def reset(self):
        self.global_dict = {}
        self.total_count = 0
        self.lengths = []


class JSWTestCaseGenerator(TestCaseGenerator):
    """基于加权JS散度的自适应随机测试生成器"""

    def __init__(
        self,
        app_name: str,
        class_variable_name: str,
        num_candidates: int = 5,
        q: int = 2,
        diversity_strategy: str = SEQUENCE_DIVERSITY_STRATEGY_NAME,
    ):
        super().__init__(app_name=app_name, class_variable_name=class_variable_name)
        self.logger = GlobalLog(logger_prefix="JSWTestCaseGenerator")
        self.num_candidates = num_candidates
        self.diversity_strategy = diversity_strategy
        self.q = q

        self.jsw_calculator = IncrementalJSW()

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

    def _get_individual_length(self, individual: Individual) -> int:
        """获取个体的方法调用语句数量（用于长度计算）"""
        method_call_statements = list(filter(
            lambda x: isinstance(x, MethodCallStatement),
            individual.statements,
        ))
        return len(method_call_statements)

    def generate(
        self, uncovered_targets: List[CoverageTarget], max_length: int = 30
    ) -> Individual:
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

        weighted_js_values = []
        for c in candidates:
            candidate_qgrams = self.compute_qgrams(individual=c)
            candidate_length = self._get_individual_length(c)
            js_k = self.jsw_calculator.compute_weighted_js(
                candidate_qgrams, candidate_length
            )
            weighted_js_values.append(js_k)

        if len(weighted_js_values) == 0 or np.isnan(weighted_js_values).all():
            index_max_js = self.random_generator.rnd_state.randint(0, len(candidates))
        else:
            weighted_js_values = np.nan_to_num(weighted_js_values, nan=-np.inf)
            index_max_js = np.argmax(weighted_js_values)

        selected_individual = candidates[index_max_js]

        assert selected_individual is not None, "Selected individual should not be None"

        # 更新全局状态
        self.store_executed_individual(individual=selected_individual)
        selected_qgrams = self.compute_qgrams(individual=selected_individual)
        selected_length = self._get_individual_length(selected_individual)
        selected_total_length = len(selected_individual.statements)
        self.jsw_calculator.update(selected_qgrams, selected_length, selected_total_length)

        return selected_individual

    def generate_new(
        self, uncovered_targets: List[CoverageTarget], max_length: int = 30
    ) -> Tuple[Individual, float]:
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

        weighted_js_values = []
        for c in candidates:
            candidate_qgrams = self.compute_qgrams(individual=c)
            candidate_length = self._get_individual_length(c)
            js_k = self.jsw_calculator.compute_weighted_js(
                candidate_qgrams, candidate_length
            )
            weighted_js_values.append(js_k)

        if len(weighted_js_values) == 0 or np.isnan(weighted_js_values).all():
            index_max_js = self.random_generator.rnd_state.randint(0, len(candidates))
        else:
            weighted_js_values = np.nan_to_num(weighted_js_values, nan=-np.inf)
            index_max_js = np.argmax(weighted_js_values)

        selected_individual = candidates[index_max_js]

        assert selected_individual is not None, "Selected individual should not be None"

        # 更新全局状态
        self.store_executed_individual(individual=selected_individual)
        selected_qgrams = self.compute_qgrams(individual=selected_individual)
        selected_length = self._get_individual_length(selected_individual)
        selected_total_length = len(selected_individual.statements)
        self.jsw_calculator.update(selected_qgrams, selected_length, selected_total_length)

        end_time = time.perf_counter()
        computation_time = end_time - start_time

        return selected_individual, computation_time

    def get_state(self) -> Optional[GeneratorState]:
        return {
            'global_dict': dict(self.jsw_calculator.global_dict),
            'total_count': self.jsw_calculator.total_count,
            'lengths': self.jsw_calculator.lengths,
            'total_lengths': self.jsw_calculator.total_lengths,
        }

    def set_state(self, generator_state: GeneratorState) -> None:
        if generator_state is not None:
            self.jsw_calculator.global_dict = defaultdict(
                int, generator_state.get('global_dict', {})
            )
            self.jsw_calculator.total_count = generator_state.get('total_count', 0)
            self.jsw_calculator.lengths = generator_state.get('lengths', [])
            self.jsw_calculator.total_lengths = generator_state.get('total_lengths', [])


if __name__ == "__main__":
    import sys
    import os
    import argparse

    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, os.getcwd())

    parser = argparse.ArgumentParser(description='查看 JSW 加权JS散度生成过程')
    parser.add_argument('--app', type=str, default='splittypie',
                        help='应用名称 (dimeshift, pagekit, petclinic, phoenix, retroboard, splittypie)')
    parser.add_argument('--iter', type=int, default=1000,
                        help='连续生成的次数')
    parser.add_argument('--candidates', type=int, default=5,
                        help='每次生成的候选用例数')
    args = parser.parse_args()

    APP_CONFIG = {
        "dimeshift": ("classUnderTest", "Dimeshift"),
        "pagekit": ("classUnderTest", "Pagekit"),
        "petclinic": ("classUnderTest", "Petclinic"),
        "phoenix": ("classUnderTest", "Phoenix"),
        "retroboard": ("classUnderTest", "Retroboard"),
        "splittypie": ("classUnderTest", "Splittypie"),
    }

    if args.app not in APP_CONFIG:
        print(f"错误: 未知的应用 '{args.app}'")
        print(f"可用的应用: {', '.join(APP_CONFIG.keys())}")
        exit(1)

    class_variable_name, display_name = APP_CONFIG[args.app]
    app_name = args.app
    # diversity_strategy = SEQUENCE_DIVERSITY_STRATEGY_NAME
    diversity_strategy = INPUT_DIVERSITY_STRATEGY_NAME

    set_random_seed(seed=0)

    generator = JSWTestCaseGenerator(
        app_name=app_name,
        class_variable_name=class_variable_name,
        num_candidates=args.candidates,
        q=2,
        diversity_strategy=diversity_strategy,
    )

    print(f"\n{'='*60}")
    print(f"应用: {display_name}")
    print(f"连续 {args.iter} 次生成过程 (每次 {args.candidates} 个候选用例)")
    print(f"{'='*60}\n")

    for iteration in range(args.iter):
        avg_l_q = 0.0
        if len(generator.jsw_calculator.lengths) > 0:
            avg_l_q = sum(generator.jsw_calculator.lengths) / len(generator.jsw_calculator.lengths)

        print(f"--- 第 {iteration + 1} 次生成 ---")
        print(f"已选集平均长度 avg_L_Q = {avg_l_q:.2f}\n")

        candidates = []
        for i in range(generator.num_candidates):
            target_edge = generator.random_generator.rnd_state.choice(
                list(generator.graph_parser.edge_names)
            )
            individual = generator.generate_individual(
                target_edge_name=target_edge,
                max_length=30
            )
            candidates.append((individual, target_edge))

        for i, (c, target_edge) in enumerate(candidates):
            candidate_qgrams = generator.compute_qgrams(individual=c)
            candidate_length = generator._get_individual_length(c)
            k = 0.0
            if candidate_length + avg_l_q > 0:
                k = candidate_length / (candidate_length + avg_l_q)
            js_k = generator.jsw_calculator.compute_weighted_js(
                candidate_qgrams, candidate_length
            )

            method_calls = [stmt for stmt in c.statements
                            if isinstance(stmt, MethodCallStatement)]
            method_names = [stmt.method_name for stmt in method_calls]

            overlap_count = len(
                set(candidate_qgrams.keys()) & set(generator.jsw_calculator.global_dict.keys())
            )
            new_gram_count = len(
                set(candidate_qgrams.keys()) - set(generator.jsw_calculator.global_dict.keys())
            )

            print(f"候选 {i+1} (目标边: {target_edge}):")
            print(f"  方法调用序列: {method_names}")
            print(f"  L_P = {candidate_length}, k = {k:.4f}, JS_k = {js_k:.6f}, 与全局重复gram数 = {overlap_count}, 新增gram数 = {new_gram_count}")
            print(f"  q-grams: {dict(candidate_qgrams)}")
            print()

        weighted_js_values = []
        for c, _ in candidates:
            candidate_qgrams = generator.compute_qgrams(individual=c)
            candidate_length = generator._get_individual_length(c)
            js_k = generator.jsw_calculator.compute_weighted_js(
                candidate_qgrams, candidate_length
            )
            weighted_js_values.append(js_k)

        if len(weighted_js_values) > 0 and not np.isnan(weighted_js_values).all():
            weighted_js_values = np.nan_to_num(weighted_js_values, nan=-np.inf)
            best_index = np.argmax(weighted_js_values)
        else:
            best_index = generator.random_generator.rnd_state.randint(0, len(candidates))

        selected = candidates[best_index][0]
        print(f"★ 选择: 候选 {best_index + 1} (加权JS散度最大 = {weighted_js_values[best_index]:.6f})")

        method_calls = [stmt for stmt in selected.statements
                        if isinstance(stmt, MethodCallStatement)]
        print(f"选中测试用例的方法调用序列:")
        for i, name in enumerate([stmt.method_name for stmt in method_calls]):
            print(f"  {i+1}. {name}")

        selected_qgrams = generator.compute_qgrams(individual=selected)
        selected_length = generator._get_individual_length(selected)
        print(f"\n选中长度 L_P = {selected_length}")
        print(f"选中的 q-grams: {dict(selected_qgrams)}")

        generator.store_executed_individual(individual=selected)
        selected_qgrams = generator.compute_qgrams(individual=selected)
        selected_length = generator._get_individual_length(selected)
        selected_total_length = len(selected.statements)
        generator.jsw_calculator.update(selected_qgrams, selected_length, selected_total_length)

        new_avg_l_q = sum(generator.jsw_calculator.lengths) / len(generator.jsw_calculator.lengths)
        new_avg_total_l_q = sum(generator.jsw_calculator.total_lengths) / len(generator.jsw_calculator.total_lengths)
        print(f"\n全局字典大小: {len(generator.jsw_calculator.global_dict)}")
        print(f"全局字典总和: {generator.jsw_calculator.total_count}")
        print(f"已选集方法调用长度列表: {generator.jsw_calculator.lengths}")
        print(f"已选集总语句长度列表: {generator.jsw_calculator.total_lengths}")
        print(f"新平均方法调用长度 avg_L_Q = {new_avg_l_q:.2f}")
        print(f"新平均总语句长度 avg_total_L_Q = {new_avg_total_l_q:.2f}")
        print(f"{'='*60}\n")