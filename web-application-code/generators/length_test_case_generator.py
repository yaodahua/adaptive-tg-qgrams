from functools import reduce
from pathlib import Path
import pickle
import time
import numpy as np
from typing import List
from config import DIMESHIFT_NAME
from executors.coverage_target import CoverageTarget
from generators.test_case_generator import TestCaseGenerator
from global_log import GlobalLog
from individuals.individual import Individual
from utils.file_utils import (
    get_class_under_test_path,
    get_coverage_targets_file,
)
from utils.randomness_utils import set_random_seed


class LengthTestCaseGenerator(TestCaseGenerator):

    def __init__(
        self, app_name: str, class_variable_name: str, num_candidates: int = 5
    ):

        super().__init__(app_name=app_name, class_variable_name=class_variable_name)
        self.logger = GlobalLog(logger_prefix="LengthTestCaseGenerator")
        self.num_candidates = num_candidates

    def generate(
        self, uncovered_targets: List[CoverageTarget], max_length: int = 30
    ) -> Individual:
        uncovered_edge_names = reduce(
            lambda acc, item: acc + [item] if item not in acc else acc,
            map(lambda x: x.method_name, uncovered_targets),
            [],
        )

        target_edge_name = self.random_generator.rnd_state.choice(uncovered_edge_names)

        if len(self.executed_individuals) == 0:
            individual = self.generate_individual(
                target_edge_name=target_edge_name, max_length=max_length
            )
            self.store_executed_individual(individual=individual)
            return individual

        # start_time = time.perf_counter()
        candidates = [
            self.generate_individual(
                target_edge_name=target_edge_name, max_length=max_length
            )
            for _ in range(self.num_candidates)
        ]
        # end_time = time.perf_counter()
        # print(f"Time to generate candidates: {end_time - start_time:.2f}s")

        max_length = np.argmax(list(map(lambda x: len(x.statements), candidates)))
        selected_individual = candidates[max_length]

        self.store_executed_individual(individual=selected_individual)

        return selected_individual


if __name__ == "__main__":
    set_random_seed(seed=0)

    app_name = DIMESHIFT_NAME

    coverage_targets_filepath = get_coverage_targets_file(app_name=app_name)

    with open(coverage_targets_filepath, "rb") as f:
        coverage_targets = pickle.load(f)

    class_filename = Path(
        get_class_under_test_path(app_name=app_name, is_instrumented=True)
    ).name
    class_filename_without_extension = class_filename.replace(".java", "")

    generator = LengthTestCaseGenerator(
        app_name=app_name,
        class_variable_name=class_filename_without_extension,
        num_candidates=30,
    )

    individual_lengths = []
    for i in range(100):
        start_time = time.perf_counter()
        individual = generator.generate(
            uncovered_targets=coverage_targets, max_length=40
        )
        print(
            f"{i} Time to generate individual: {time.perf_counter() - start_time:2f}s"
        )
        individual_lengths.append(len(individual.statements))

    print(f"Average individual lengths: {np.mean(individual_lengths)}")
