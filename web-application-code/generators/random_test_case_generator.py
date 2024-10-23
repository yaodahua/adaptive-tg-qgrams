from functools import reduce
from pathlib import Path
import pickle
from typing import List, Optional
from config import DIMESHIFT_NAME
from executors.coverage_target import CoverageTarget
from generators.test_case_generator import TestCaseGenerator
from global_log import GlobalLog
from individuals.individual import Individual
from type_aliases import GeneratorState
from utils.file_utils import (
    get_class_under_test_path,
    get_coverage_targets_file,
)
from utils.randomness_utils import set_random_seed


class RandomTestCaseGenerator(TestCaseGenerator):

    def __init__(self, app_name: str, class_variable_name: str):

        super().__init__(app_name=app_name, class_variable_name=class_variable_name)
        self.logger = GlobalLog(logger_prefix="RandomTestCaseGenerator")

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
        random_walk = self.graph_parser.get_random_walk_from_index_to_target_edge(
            target_edge_name=target_edge_name, max_length=max_length
        )
        assert len(random_walk) > 0, "Random walk should not be empty"
        assert (
            target_edge_name in random_walk[-1]
        ), f"Random walk should end at target edge: {target_edge_name} != {random_walk[-1]}, len(random_walk)={len(random_walk)}"

        statements = self.build_method_calls(method_names=random_walk)
        return Individual(statements=statements)

    def get_state(self) -> Optional[GeneratorState]:
        return None

    # random test generator has no state
    def set_state(self, generator_state: GeneratorState) -> None:
        pass


if __name__ == "__main__":
    set_random_seed(seed=1172537062)

    app_name = DIMESHIFT_NAME

    coverage_targets_filepath = get_coverage_targets_file(app_name=app_name)

    with open(coverage_targets_filepath, "rb") as f:
        coverage_targets = pickle.load(f)

    class_filename = Path(
        get_class_under_test_path(app_name=app_name, is_instrumented=True)
    ).name
    class_filename_without_extension = class_filename.replace(".java", "")

    for i in range(100):
        random_generator = RandomTestCaseGenerator(
            app_name=app_name, class_variable_name=class_filename_without_extension
        )
        individual = random_generator.generate(
            uncovered_targets=coverage_targets, max_length=30
        )
