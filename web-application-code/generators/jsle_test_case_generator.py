"""
基于JS散度+边界编码的自适应随机测试(JSLE)生成器

本文件实现了基于Jensen-Shannon散度的自适应随机测试生成器,使用边界编码方案.
主要特点:
1. 使用JS散度衡量测试用例与已有测试套件的多样性
2. 支持三种边界编码方案: SCHEME_A, SCHEME_B, SCHEME_C
3. 增量更新全局q-gram频率分布
4. 从候选测试用例中选择JS散度最大的个体

边界编码方案:
- SCHEME_A: [START, A, B, C, END] -> (START), (A,B), (B,C), (END)
- SCHEME_B: [START, A, B, C, END] -> (START,A), (A,B), (B,C), (C,END)
- SCHEME_C: [START, A, B, C, END] -> START, (A,B), (B,C), (C,END)
"""

import math
from collections import defaultdict
from enum import Enum
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


class BoundaryScheme(Enum):
    SCHEME_A = "independent_side"
    SCHEME_B = "combined_side"
    SCHEME_C = "hybrid"


BOUNDARY_START = "STARTBOUNDARY"
BOUNDARY_END = "ENDBOUNDARY"
EMPTY = "EMPTY"


def compute_js_divergence(global_dict, candidate_dict, global_total=None, candidate_total=None):
    if global_total is None:
        global_total = sum(global_dict.values())
    if candidate_total is None:
        candidate_total = sum(candidate_dict.values())
    
    if global_total == 0 or candidate_total == 0:
        return 0.0
    
    if global_total == 0 and candidate_total > 0:
        return 1.0
    
    inv_global_total = 1.0 / global_total
    inv_candidate_total = 1.0 / candidate_total
    
    if len(global_dict) < len(candidate_dict):
        smaller_dict, larger_dict = global_dict, candidate_dict
    else:
        smaller_dict, larger_dict = candidate_dict, global_dict
    
    epsilon = 1e-10
    js_div = 0.0
    
    for gram in smaller_dict:
        g_count = global_dict.get(gram, 0)
        c_count = candidate_dict.get(gram, 0)
        
        p = g_count * inv_global_total
        q = c_count * inv_candidate_total
        m = (p + q) * 0.5
        
        if p > epsilon and m > epsilon:
            js_div += p * math.log(p / m)
        
        if q > epsilon and m > epsilon:
            js_div += q * math.log(q / m)
    
    for gram in larger_dict:
        if gram not in smaller_dict:
            g_count = global_dict.get(gram, 0)
            c_count = candidate_dict.get(gram, 0)
            
            p = g_count * inv_global_total
            q = c_count * inv_candidate_total
            m = (p + q) * 0.5
            
            if p > epsilon and m > epsilon:
                js_div += p * math.log(p / m)# math.log默认底数为e
            
            if q > epsilon and m > epsilon:
                js_div += q * math.log(q / m)
    
    js_div *= 0.5
    
    return js_div


class IncrementalJS:
    def __init__(self):
        self.global_dict = defaultdict(int)
        self.total_count = 0
    
    def update(self, new_dict):
        for gram, count in new_dict.items():
            self.global_dict[gram] += count
        self.total_count += sum(new_dict.values())
    
    def compute_js(self, candidate_dict):
        candidate_total = sum(candidate_dict.values())
        return compute_js_divergence(
            self.global_dict, 
            candidate_dict, 
            global_total=self.total_count,
            candidate_total=candidate_total
        )
    
    def reset(self):
        self.global_dict = {}
        self.total_count = 0


class JSLETestCaseGenerator(TestCaseGenerator):
    def __init__(
        self,
        app_name: str,
        class_variable_name: str,
        num_candidates: int = 5,
        q: int = 2,
        diversity_strategy: str = SEQUENCE_DIVERSITY_STRATEGY_NAME,
        boundary_scheme: BoundaryScheme = BoundaryScheme.SCHEME_A,
    ):
        super().__init__(app_name=app_name, class_variable_name=class_variable_name)
        self.logger = GlobalLog(logger_prefix="JSLETestCaseGenerator")
        self.num_candidates = num_candidates
        self.diversity_strategy = diversity_strategy
        self.q = q
        self.boundary_scheme = boundary_scheme
        
        self.js_calculator = IncrementalJS()
        
        assert (
            diversity_strategy in DIVERSITY_STRATEGY_NAMES
        ), "Invalid diversity strategy"

    def compute_qgrams(
        self, individual: Individual
    ) -> Dict[str, int]:
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

        return self._encode_with_boundary(method_strs, self.boundary_scheme, self.q)

    def _encode_with_boundary(
        self, method_strs: List[str], scheme: BoundaryScheme, q: int
    ) -> Dict[str, int]:
        freq_dict = defaultdict(int)
        
        if not method_strs:
            return dict(freq_dict)
        
        if scheme == BoundaryScheme.SCHEME_A:
            # extended = [BOUNDARY_START] + method_strs + [BOUNDARY_END]
            if len(method_strs) >= 1:
                freq_dict[(BOUNDARY_START,EMPTY)] += 1
                freq_dict[(BOUNDARY_END,EMPTY)] += 1
            
            for i in range(len(method_strs) - q + 1):
                gram = tuple(method_strs[i:i+q])
                freq_dict[gram] += 1
        
        elif scheme == BoundaryScheme.SCHEME_B:
            extended = [BOUNDARY_START] + method_strs + [BOUNDARY_END]
            for i in range(len(extended) - q + 1):
                gram = tuple(extended[i:i+q])
                freq_dict[gram] += 1
        
        elif scheme == BoundaryScheme.SCHEME_C:
            extended = [BOUNDARY_START] + method_strs + [BOUNDARY_END]
            
            if len(method_strs) >= 1:
                freq_dict[(BOUNDARY_START, EMPTY)] += 1
            
            for i in range(len(method_strs)-1):
                gram = tuple(method_strs[i:i+q])
                freq_dict[gram] += 1
            
            if len(method_strs) >= 1:
                freq_dict[(method_strs[-1], BOUNDARY_END)] += 1
        
        return dict(freq_dict)

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

        js_divergences = []
        for c in candidates:
            candidate_qgrams = self.compute_qgrams(individual=c)
            js_div = self.js_calculator.compute_js(candidate_qgrams)
            js_divergences.append(js_div)

        if len(js_divergences) == 0 or np.isnan(js_divergences).all():
            index_max_js = self.random_generator.rnd_state.randint(0, len(candidates))
        else:
            js_divergences = np.nan_to_num(js_divergences, nan=-np.inf)
            index_max_js = np.argmax(js_divergences)
        
        selected_individual = candidates[index_max_js]

        assert selected_individual is not None, "Selected individual should not be None"

        self.store_executed_individual(individual=selected_individual)
        selected_qgrams = self.compute_qgrams(individual=selected_individual)
        self.js_calculator.update(selected_qgrams)

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

        js_divergences = []
        for c in candidates:
            candidate_qgrams = self.compute_qgrams(individual=c)
            js_div = self.js_calculator.compute_js(candidate_qgrams)
            js_divergences.append(js_div)

        if len(js_divergences) == 0 or np.isnan(js_divergences).all():
            index_max_js = self.random_generator.rnd_state.randint(0, len(candidates))
        else:
            js_divergences = np.nan_to_num(js_divergences, nan=-np.inf)
            index_max_js = np.argmax(js_divergences)
        
        selected_individual = candidates[index_max_js]

        assert selected_individual is not None, "Selected individual should not be None"

        self.store_executed_individual(individual=selected_individual)
        selected_qgrams = self.compute_qgrams(individual=selected_individual)
        self.js_calculator.update(selected_qgrams)

        end_time = time.perf_counter()
        js_computation_time = end_time - start_time

        return selected_individual, js_computation_time

    def get_state(self) -> Optional[GeneratorState]:
        return {
            'global_dict': dict(self.js_calculator.global_dict),
            'total_count': self.js_calculator.total_count
        }

    def set_state(self, generator_state: GeneratorState) -> None:
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

    generator = JSLETestCaseGenerator(
        app_name=app_name,
        class_variable_name="app",
        num_candidates=5,
        q=2,
        diversity_strategy=diversity_strategy,
        boundary_scheme=BoundaryScheme.SCHEME_A,
    )

    print(f"Testing JSLE Generator with {len(coverage_targets)} coverage targets")
    
    for i in range(5):
        individual = generator.generate(uncovered_targets=coverage_targets)
        print(f"Generated individual {i+1}: {individual}")
