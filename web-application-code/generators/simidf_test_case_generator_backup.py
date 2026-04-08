'''
参考global_idf算法.txt 实现针对web测试的SimIDF算法

'''

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




class SimIDFTestCaseGenerator(TestCaseGenerator):
    """
    SimIDF测试用例生成器 基于SimIDF自适应随机测试算法
    使用全局聚合向量近似存档多样性，复杂度较低
    """

    def __init__(
        self,
        app_name: str,
        class_variable_name: str,
        num_candidates: int = 5,
        diversity_strategy: str = SEQUENCE_DIVERSITY_STRATEGY_NAME,
        alpha: float = 0.1,  # 滑动平均参数
    ):

        super().__init__(app_name=app_name, class_variable_name=class_variable_name)
        self.logger = GlobalLog(logger_prefix="SimIDFTestCaseGenerator")
        self.num_candidates = num_candidates
        self.diversity_strategy = diversity_strategy
        self.alpha = alpha
        
        # SimIDF核心数据结构（遵循global_idf算法.txt文档定义）
        self.global_tf_vector: Dict[str, float] = {}  # 全局TF向量（词频向量）
        self.doc_freq: Dict[str, int] = {}  # 文档频率统计
        self.total_tests = 0  # 总测试用例数
        self.archive: List[Individual] = []  # 测试用例存档

        assert (
            diversity_strategy in DIVERSITY_STRATEGY_NAMES
        ), "Invalid diversity strategy"

    def _extract_features(self, individual: Individual) -> List[str]:
        """
        从测试用例中提取2-gram特征
        支持两种多样性策略：序列多样性和输入多样性
        """
        if self.diversity_strategy == SEQUENCE_DIVERSITY_STRATEGY_NAME:
            # 序列多样性策略：仅使用方法名序列
            method_sequence = []
            for statement in individual.statements:
                if isinstance(statement, MethodCallStatement):
                    method_sequence.append(statement.method_name)
            
            # 提取2-gram特征（方法调用序列的相邻组合）
            ngrams = []
            for i in range(len(method_sequence) - 1):
                ngram = f"({method_sequence[i]},{method_sequence[i+1]})"
                ngrams.append(ngram)
            
            return ngrams
            
        elif self.diversity_strategy == INPUT_DIVERSITY_STRATEGY_NAME:
            # 输入多样性策略：使用方法名和参数信息
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
            
            # 提取2-gram特征（包含参数信息的方法序列）
            ngrams = []
            for i in range(len(method_strs) - 1):
                ngram = f"({method_strs[i]},{method_strs[i+1]})"
                ngrams.append(ngram)
            
            return ngrams
            
        else:
            raise RuntimeError(f"Unknown diversity strategy: {self.diversity_strategy}")

    def _compute_simidf_score(self, individual: Individual) -> float:
        """
        计算SimIDF得分 基于TF-IDF向量和余弦相似度的多样性度量
        严格遵循global_idf算法.txt文档中的TF-IDF计算逻辑
        """
        features = self._extract_features(individual)
        
        if not features:
            return 0.0
            
        # 计算当前测试用例的TF向量（词频向量）- 严格遵循算法文档进行归一化
        current_tf_vector: Dict[str, float] = {}
        total_features = len(features)
        for feature in features:
            if feature not in current_tf_vector:
                current_tf_vector[feature] = 0
            current_tf_vector[feature] += 1.0 / total_features  # 归一化处理
        
        # 如果还没有任何测试用例，返回最大多样性
        if self.total_tests == 0:
            return 1.0
            
        # 计算TF-IDF向量
        current_tfidf_vector: Dict[str, float] = {}
        global_tfidf_vector: Dict[str, float] = {}
        
        # 计算当前测试用例的TF-IDF向量
        for feature, tf in current_tf_vector.items():
            # 计算IDF（使用平滑处理）
            df = self.doc_freq.get(feature, 0)
            idf = np.log((self.total_tests + 1) / (df + 0.5))
            current_tfidf_vector[feature] = tf * idf
        
        # 计算全局TF-IDF向量
        for feature, tf in self.global_tf_vector.items():
            df = self.doc_freq.get(feature, 0)
            idf = np.log((self.total_tests + 1) / (df + 0.5))
            global_tfidf_vector[feature] = tf * idf
        
        # 计算余弦相似度（基于TF-IDF向量）
        dot_product = 0.0
        current_norm = 0.0
        global_norm = 0.0
        
        # 计算点积，只计算当前测试用例和全局向量中都有的特征
        for feature, tfidf in current_tfidf_vector.items():
            current_norm += tfidf * tfidf
            if feature in global_tfidf_vector:
                dot_product += tfidf * global_tfidf_vector[feature]
        
        # 计算全局TF-IDF向量模长
        for tfidf in global_tfidf_vector.values():
            global_norm += tfidf * tfidf
            
        # 避免除零
        if current_norm == 0 or global_norm == 0:
            return 1.0
            
        # 余弦相似度
        cosine_similarity = dot_product / (np.sqrt(current_norm) * np.sqrt(global_norm))
        
        # 计算多样性得分（1 - 相似度）
        diversity_score = 1.0 - cosine_similarity
        
        # 返回多样性得分
        return diversity_score

    def _update_global_vector(self, individual: Individual) -> None:
        """
        使用精确滑动平均更新全局TF向量和文档频率
        严格遵循global_idf算法.txt文档中的滑动平均机制
        """
        features = self._extract_features(individual)
        
        if not features:
            return
            
        # 计算当前测试用例的TF向量（词频向量）- 严格遵循算法文档进行归一化
        current_tf_vector: Dict[str, float] = {}
        total_features = len(features)
        for feature in features:
            if feature not in current_tf_vector:
                current_tf_vector[feature] = 0
            current_tf_vector[feature] += 1.0 / total_features  # 归一化处理 
        
        # 更新文档频率
        for feature in set(features):
            if feature not in self.doc_freq:
                self.doc_freq[feature] = 0
            self.doc_freq[feature] += 1
        
        # 更新全局TF向量（精确滑动平均）
        for feature, tf in current_tf_vector.items():
            if feature not in self.global_tf_vector:
                self.global_tf_vector[feature] = 0.0
            # 精确滑动平均：新值 = (旧值 * total_tests + 当前值) / (total_tests + 1)
            if self.total_tests > 0:
                self.global_tf_vector[feature] = (self.global_tf_vector[feature] * self.total_tests + tf) / (self.total_tests + 1)
            else:
                self.global_tf_vector[feature] = tf
        
        # 更新总测试用例数
        self.total_tests += 1
        
        # 添加到存档
        self.archive.append(individual)

    def generate(
        self, uncovered_targets: List[CoverageTarget], max_length: int = 30
    ) -> Individual:
        """
        生成测试用例 选择SimIDF得分最高的候选
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
        # start_time = time.perf_counter()

        simidf_scores = []
        for candidate in candidates:
            simidf_scores.append(self._compute_simidf_score(candidate))

        index_max_diversity = np.argmax(simidf_scores)
        selected_individual = candidates[index_max_diversity]

        assert selected_individual is not None, "Selected individual should not be None"

        self.store_executed_individual(individual=selected_individual)
        self._update_global_vector(individual=selected_individual)

        # end_time = time.perf_counter()
        # print(f"SimIDF computation time: {end_time - start_time:.5f}s")

        return selected_individual

    def generate_new(
        self, uncovered_targets: List[CoverageTarget], max_length: int = 30
    ) -> Tuple[Individual, float]:
        """
        生成测试用例并返回计算时间
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

        simidf_scores = []
        for candidate in candidates:
            simidf_scores.append(self._compute_simidf_score(candidate))

        index_max_diversity = np.argmax(simidf_scores)
        selected_individual = candidates[index_max_diversity]

        assert selected_individual is not None, "Selected individual should not be None"

        self.store_executed_individual(individual=selected_individual)
        self._update_global_vector(individual=selected_individual)

        end_time = time.perf_counter()

        return selected_individual, end_time - start_time

    def get_state(self) -> Optional[GeneratorState]:
        """获取生成器状态"""
        return {
            'global_tf_vector': self.global_tf_vector,
            'doc_freq': self.doc_freq,
            'total_tests': self.total_tests,
            'archive': self.archive
        }

    def set_state(self, generator_state: GeneratorState) -> None:
        """设置生成器状态"""
        if isinstance(generator_state, dict):
            self.global_tf_vector = generator_state.get('global_tf_vector', {})
            self.doc_freq = generator_state.get('doc_freq', {})
            self.total_tests = generator_state.get('total_tests', 0)
            self.archive = generator_state.get('archive', [])


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

    generator = SimIDFTestCaseGenerator(
        app_name=app_name,
        class_variable_name=class_filename_without_extension,
        num_candidates=30,
        diversity_strategy=diversity_strategy,
        alpha=0.1,
    )

    individual_lengths = []
    simidf_computation_times = []
    for i in range(100):
        start_time = time.perf_counter()
        individual, simidf_computation_time = generator.generate_new(
            uncovered_targets=coverage_targets, max_length=40
        )
        simidf_computation_times.append(simidf_computation_time)
        print(
            f"{i} Time to generate individual: {time.perf_counter() - start_time:2f}s"
        )
        individual_lengths.append(len(individual.statements))

    print(
        np.mean(simidf_computation_times),
        np.median(simidf_computation_times),
        np.max(simidf_computation_times),
    )

    print(f"Average individual lengths: {np.mean(individual_lengths)}")