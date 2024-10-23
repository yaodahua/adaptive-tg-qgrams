from functools import reduce
from pathlib import Path
import pickle
import time
import numpy as np
from scipy.stats import entropy
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


class QgramsTestCaseGenerator(TestCaseGenerator):

    def __init__(
        self,
        app_name: str,
        class_variable_name: str,
        num_candidates: int = 5,
        q: int = 2,
        diversity_strategy: str = SEQUENCE_DIVERSITY_STRATEGY_NAME,
    ):

        super().__init__(app_name=app_name, class_variable_name=class_variable_name)
        self.logger = GlobalLog(logger_prefix="QgramsTestCaseGenerator")
        self.num_candidates = num_candidates
        self.qgram_counts = dict()
        self.diversity_strategy = diversity_strategy
        self.q = q

        assert (
            diversity_strategy in DIVERSITY_STRATEGY_NAMES
        ), "Invalid diversity strategy"

    def compute_qgrams(
        self, qgram_counts: Dict[Tuple[str], int], individual: Individual
    ) -> Dict[Tuple[str], int]:

        if self.diversity_strategy == SEQUENCE_DIVERSITY_STRATEGY_NAME:
            method_strs = list(
                map(
                    # lambda x: x.to_string().split(".")[-1],
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

        qgram_counts_local = dict(qgram_counts)

        for i in range(len(method_strs) - self.q + 1):
            qgram = tuple(method_strs[i : i + self.q])
            if qgram not in qgram_counts_local:
                qgram_counts_local[qgram] = 0
            qgram_counts_local[qgram] += 1

        return qgram_counts_local

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
        # start_time = time.perf_counter()

        entropies = []
        for c in candidates:

            qgram_counts_local = dict(self.qgram_counts)
            qgram_counts_local = self.compute_qgrams(
                qgram_counts=qgram_counts_local, individual=c
            )

            entropies.append(entropy(list(qgram_counts_local.values()), base=2))

        index_max_entropy = np.argmax(entropies)
        selected_individual = candidates[index_max_entropy]

        assert selected_individual is not None, "Selected individual should not be None"

        self.store_executed_individual(individual=selected_individual)
        self.qgram_counts = self.compute_qgrams(
            qgram_counts=self.qgram_counts, individual=selected_individual
        )

        # end_time = time.perf_counter()
        # print(f"Qgrams computation time: {end_time - start_time:.5f}s")

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

        entropies = []
        for c in candidates:

            qgram_counts_local = dict(self.qgram_counts)
            qgram_counts_local = self.compute_qgrams(
                qgram_counts=qgram_counts_local, individual=c
            )

            entropies.append(entropy(list(qgram_counts_local.values()), base=2))

        index_max_entropy = np.argmax(entropies)
        selected_individual = candidates[index_max_entropy]

        assert selected_individual is not None, "Selected individual should not be None"

        self.store_executed_individual(individual=selected_individual)
        self.qgram_counts = self.compute_qgrams(
            qgram_counts=self.qgram_counts, individual=selected_individual
        )

        end_time = time.perf_counter()
        # print(f"Qgrams computation time: {end_time - start_time:.5f}s")

        return selected_individual, end_time - start_time

    def get_state(self) -> Optional[GeneratorState]:
        return self.qgram_counts

    def set_state(self, generator_state: GeneratorState) -> None:
        self.qgram_counts = dict(generator_state)


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

    generator = QgramsTestCaseGenerator(
        app_name=app_name,
        class_variable_name=class_filename_without_extension,
        num_candidates=30,
        diversity_strategy=diversity_strategy,
        q=2,
    )

    individual_lengths = []
    entropy_computation_times = []
    for i in range(4000):
        start_time = time.perf_counter()
        individual, entropy_computation_time = generator.generate_new(
            uncovered_targets=coverage_targets, max_length=40
        )
        entropy_computation_times.append(entropy_computation_time)
        print(
            f"{i} Time to generate individual: {time.perf_counter() - start_time:2f}s"
        )
        individual_lengths.append(len(individual.statements))
        # coverage_targets_with_method_name = list(
        #     filter(
        #         lambda x: x.method_name == individual.statements[-1].method_name,
        #         coverage_targets,
        #     )
        # )

    # values = np.array(list(generator.qgram_counts.values()))
    # print(len(values[values > 1]) / len(values))
    print(
        np.mean(entropy_computation_times),
        np.median(entropy_computation_times),
        np.max(entropy_computation_times),
    )

    print(f"Average individual lengths: {np.mean(individual_lengths)}")
