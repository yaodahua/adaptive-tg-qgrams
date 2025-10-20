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


class TFIDFTestCaseGenerator(TestCaseGenerator):
    """
    TF-IDF测试用例生成器 基于完整的TF-IDF计算
    维护完整的二元组频率统计，复杂度较高但精度更高
    """

    def __init__(
        self,
        app_name: str,
        class_variable_name: str,
        num_candidates: int = 5,
        diversity_strategy: str = SEQUENCE_DIVERSITY_STRATEGY_NAME,
        q: int = 2,  # q-gram的大小
    ):

        super().__init__(app_name=app_name, class_variable_name=class_variable_name)
        self.logger = GlobalLog(logger_prefix="TFIDFTestCaseGenerator")
        self.num_candidates = num_candidates
        self.diversity_strategy = diversity_strategy
        self.q = q
        
        # TF-IDF核心数据结构
        self.qgram_counts: Dict[Tuple[str], int] = {}  # 全局q-gram频率统计
        self.document_qgrams: List[Dict[Tuple[str], int]] = []  # 每个文档的q-gram统计
        self.total_documents = 0  # 总文档数

        assert (
            diversity_strategy in DIVERSITY_STRATEGY_NAMES
        ), "Invalid diversity strategy"

    def _extract_qgrams(self, individual: Individual) -> Dict[Tuple[str], int]:
        """
        从测试用例中提取q-gram
        """
        if self.diversity_strategy == SEQUENCE_DIVERSITY_STRATEGY_NAME:
            # 序列多样性策略：提取方法名序列
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
            # 输入多样性策略：提取方法名和参数信息
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

        # 提取q-gram
        qgram_counts_local: Dict[Tuple[str], int] = {}
        for i in range(len(method_strs) - self.q + 1):
            qgram = tuple(method_strs[i : i + self.q])
            if qgram not in qgram_counts_local:
                qgram_counts_local[qgram] = 0
            qgram_counts_local[qgram] += 1

        return qgram_counts_local

    def _compute_tfidf_score(self, individual: Individual) -> float:
        """
        计算TF-IDF得分 基于信息熵的多样性度量
        """
        if self.total_documents == 0:
            # 如果没有历史文档，返回最大多样性
            return 1.0
            
        # 提取当前测试用例的q-gram
        current_qgrams = self._extract_qgrams(individual)
        
        if not current_qgrams:
            return 0.0
            
        # 计算TF-IDF向量
        tfidf_vector = []
        
        for qgram, tf in current_qgrams.items():
            # 计算TF（词频）
            tf_normalized = tf / sum(current_qgrams.values())
            
            # 计算IDF（逆文档频率）
            df = sum(1 for doc_qgrams in self.document_qgrams if qgram in doc_qgrams)
            idf = np.log((self.total_documents + 1) / (df + 1)) + 1  # 平滑处理
            
            tfidf_vector.append(tf_normalized * idf)
        
        # 如果向量为空，返回0
        if not tfidf_vector:
            return 0.0
            
        # 计算信息熵作为多样性度量
        # 归一化TF-IDF向量
        tfidf_sum = sum(tfidf_vector)
        if tfidf_sum == 0:
            return 0.0
            
        normalized_tfidf = [v / tfidf_sum for v in tfidf_vector]
        
        # 计算信息熵（熵值越高，多样性越好）
        entropy_value = 0.0
        for p in normalized_tfidf:
            if p > 0:
                entropy_value -= p * np.log(p)
        
        # 归一化熵值到[0,1]范围
        max_entropy = np.log(len(normalized_tfidf)) if len(normalized_tfidf) > 0 else 0
        if max_entropy > 0:
            normalized_entropy = entropy_value / max_entropy
        else:
            normalized_entropy = 0.0
            
        return normalized_entropy

    def _update_global_statistics(self, individual: Individual) -> None:
        """
        更新全局统计信息
        """
        current_qgrams = self._extract_qgrams(individual)
        
        # 更新全局q-gram频率
        for qgram, count in current_qgrams.items():
            if qgram not in self.qgram_counts:
                self.qgram_counts[qgram] = 0
            self.qgram_counts[qgram] += count
        
        # 添加当前文档的q-gram统计
        self.document_qgrams.append(current_qgrams)
        self.total_documents += 1
        
        # 限制文档数量以避免内存爆炸（可选优化）
        if len(self.document_qgrams) > 1000:  # 保留最近1000个文档
            self.document_qgrams = self.document_qgrams[-1000:]
            self.total_documents = 1000

    def generate(
        self, uncovered_targets: List[CoverageTarget], max_length: int = 30
    ) -> Individual:
        """
        生成测试用例 选择TF-IDF得分最高的候选
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

        tfidf_scores = []
        for candidate in candidates:
            tfidf_scores.append(self._compute_tfidf_score(candidate))

        index_max_diversity = np.argmax(tfidf_scores)
        selected_individual = candidates[index_max_diversity]

        assert selected_individual is not None, "Selected individual should not be None"

        self.store_executed_individual(individual=selected_individual)
        self._update_global_statistics(individual=selected_individual)

        # end_time = time.perf_counter()
        # print(f"TF-IDF computation time: {end_time - start_time:.5f}s")

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

        tfidf_scores = []
        for candidate in candidates:
            tfidf_scores.append(self._compute_tfidf_score(candidate))

        index_max_diversity = np.argmax(tfidf_scores)
        selected_individual = candidates[index_max_diversity]

        assert selected_individual is not None, "Selected individual should not be None"

        self.store_executed_individual(individual=selected_individual)
        self._update_global_statistics(individual=selected_individual)

        end_time = time.perf_counter()

        return selected_individual, end_time - start_time

    def get_state(self) -> Optional[GeneratorState]:
        """获取生成器状态"""
        return {
            'qgram_counts': self.qgram_counts,
            'document_qgrams': self.document_qgrams,
            'total_documents': self.total_documents
        }

    def set_state(self, generator_state: GeneratorState) -> None:
        """设置生成器状态"""
        if isinstance(generator_state, dict):
            self.qgram_counts = generator_state.get('qgram_counts', {})
            self.document_qgrams = generator_state.get('document_qgrams', [])
            self.total_documents = generator_state.get('total_documents', 0)


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

    generator = TFIDFTestCaseGenerator(
        app_name=app_name,
        class_variable_name=class_filename_without_extension,
        num_candidates=30,
        diversity_strategy=diversity_strategy,
        q=2,
    )

    individual_lengths = []
    tfidf_computation_times = []
    for i in range(100):
        start_time = time.perf_counter()
        individual, tfidf_computation_time = generator.generate_new(
            uncovered_targets=coverage_targets, max_length=40
        )
        tfidf_computation_times.append(tfidf_computation_time)
        print(
            f"{i} Time to generate individual: {time.perf_counter() - start_time:2f}s"
        )
        individual_lengths.append(len(individual.statements))

    print(
        np.mean(tfidf_computation_times),
        np.median(tfidf_computation_times),
        np.max(tfidf_computation_times),
    )

    print(f"Average individual lengths: {np.mean(individual_lengths)}")