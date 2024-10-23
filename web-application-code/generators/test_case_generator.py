from abc import ABC, abstractmethod
import importlib
import os
from pathlib import Path
from typing import List, Optional, Tuple, Union
from config import (
    APP_NAMES,
    DIMESHIFT_NAME,
    DISTANCE_GENERATOR_NAME,
    GENERATOR_NAMES,
    LENGTH_GENERATOR_NAME,
    QGRAMS_GENERATOR_NAME,
)
from executors.coverage_target import CoverageTarget
from global_log import GlobalLog
from individuals.individual import Individual
from parsing.class_parser import ClassParser
from parsing.graph_parser import GraphParser
from parsing.parsing_utils import find_classes_implementing_interface
from statements.class_declaration_statement import ClassDeclarationStatement
from statements.enum_statement import EnumStatement
from statements.method_call_statement import MethodCallStatement
from statements.reset_statement import ResetStatement
from statements.statement import Statement
from type_aliases import GeneratorState
from utils.file_utils import get_class_under_test_path, get_graph_path
from utils.randomness_utils import RandomGenerator


class TestCaseGenerator(ABC):

    def __init__(self, app_name: str, class_variable_name: str):

        assert app_name in APP_NAMES, f"App name {app_name} is not valid"

        self.app_name = app_name
        self.class_variable_name = class_variable_name
        self.graph_parser = GraphParser(
            graph_dot_file=get_graph_path(app_name=app_name)
        )
        self.logger = GlobalLog(logger_prefix="TestCaseGenerator")
        self.class_under_test_cu = ClassParser(app_name=app_name)
        self.random_generator = RandomGenerator.get_instance()
        self.executed_individuals: List[Individual] = []
        self.final_test_suite: List[Tuple[Individual, List[CoverageTarget]]] = []

    def store_executed_individual(self, individual: Individual) -> None:
        self.executed_individuals.append(individual)

    def get_final_test_suite(self) -> List[Tuple[Individual, List[CoverageTarget]]]:
        return self.final_test_suite

    def set_final_test_suite(
        self, final_test_suite: List[Tuple[Individual, List[CoverageTarget]]]
    ) -> None:
        self.final_test_suite = [
            (individual.clone(), [ct.clone() for ct in coverage_targets])
            for individual, coverage_targets in final_test_suite
        ]

    def update_final_test_suite(
        self, individual: Individual, covered_targets: List[CoverageTarget]
    ) -> None:
        new_individual = individual.clone()
        new_individual.statements = Individual.remove_dangling_statements(
            statements=individual.statements
        )
        self.final_test_suite.append((new_individual, covered_targets))

    @staticmethod
    def parse_final_test_suite(test_suite_filepath: str) -> List[Individual]:
        with open(test_suite_filepath, "r") as f:
            lines = f.readlines()

        individuals_strings = dict()
        count = 0
        for line in lines:
            if line.startswith("/*") or line.startswith("*"):
                if line.startswith("****"):
                    count += 1
                continue

            if str(count) not in individuals_strings:
                individuals_strings[str(count)] = []

            individuals_strings[str(count)].append(line.strip())

        return [
            Individual.parse_statement_strings(statement_strings=individual_string)
            for individual_string in individuals_strings.values()
        ]

    def write_final_test_suite(
        self, covered_targets: List[CoverageTarget]
    ) -> List[str]:
        assert len(self.final_test_suite) > 0, "Final test suite is empty"
        # sorting by the test case that covers the highest number of targets
        sorted_test_suite = sorted(
            self.final_test_suite, key=lambda x: len(set(x[1])), reverse=True
        )
        i = 0
        covered_targets_local = set()
        minimized_test_suite: List[Individual] = []
        while len(covered_targets_local) < len(covered_targets):
            current_coverage_targets = sorted_test_suite[i][1]
            if any(
                filter(
                    lambda x: x not in covered_targets_local, current_coverage_targets
                )
            ):
                self.logger.info(
                    f"Adding test case with id {sorted_test_suite[i][0].id} with # unique targets "
                    f"covered {len(set(current_coverage_targets))}"
                )
                minimized_test_suite.append(sorted_test_suite[i])
                covered_targets_local.update(current_coverage_targets)
                self.logger.info(
                    f"Total targets covered: {len(covered_targets_local)}/{len(covered_targets)}"
                )
            i += 1

        all_strings = []
        for individual, coverage_targets in minimized_test_suite:
            all_strings.append("/*")
            for ct in coverage_targets:
                all_strings.append(f"* {ct.__str__()}")
            all_strings.append("*/")
            all_strings.append("\n".join(individual.to_string()))
            all_strings.append("*" * 20)

        return "\n".join(all_strings)

    @abstractmethod
    def generate(
        self, uncovered_targets: List[CoverageTarget], max_length: int
    ) -> Individual:
        pass

    def generate_individual(
        self, target_edge_name: str, max_length: int = 30
    ) -> Individual:
        random_walk = self.graph_parser.get_random_walk_from_index_to_target_edge(
            target_edge_name=target_edge_name, max_length=max_length
        )
        assert len(random_walk) > 0, "Random walk should not be empty"
        assert (
            target_edge_name in random_walk[-1]
        ), f"Random walk should end at target edge: {target_edge_name} != {random_walk[-1]}, len(random_walk)={len(random_walk)}"

        statements = self.build_method_calls(method_names=random_walk)
        return Individual(statements=statements)

    def _handle_input_class(
        self,
        input_class: ClassParser,
        class_name: str,
        previous_values: List[Tuple[str, Union[int, str]]],
        counter: int,
    ) -> Tuple[Statement, Union[int, str]]:

        value = None
        usable_previous_values = list(
            map(
                lambda x: x[1],
                filter(lambda x: x[0] == class_name, previous_values),
            )
        )

        if len(input_class.get_enum_values()) > 0:

            if (
                self.random_generator.rnd_state.rand() < 0.5
                and len(usable_previous_values) > 0
            ):
                # reuse value
                enum_value = self.random_generator.rnd_state.choice(
                    usable_previous_values
                )
            else:
                enum_value = self.random_generator.rnd_state.choice(
                    input_class.get_enum_values()
                )
            statement = EnumStatement(
                class_name=class_name,
                value=enum_value,
                counter=counter,
            )
            value = enum_value

        elif input_class.is_range_type():

            if (
                self.random_generator.rnd_state.rand() < 0.5
                and len(usable_previous_values) > 0
            ):
                # reuse value
                range_value = self.random_generator.rnd_state.choice(
                    usable_previous_values
                )
            else:
                intervals = input_class.get_intervals_for_range_type()
                range_value = self.random_generator.rnd_state.randint(
                    low=intervals[0] - 1, high=intervals[1] + 1
                )

            statement = ClassDeclarationStatement(
                class_name=class_name, value=range_value, counter=counter
            )
            value = range_value

        else:
            raise NotImplementedError(
                f"Input class {class_name} is not an enum nor a range"
            )

        return statement, value

    def build_method_calls(self, method_names: List[str]) -> List[Statement]:
        class_declaration_statement = ClassDeclarationStatement(
            class_name=self.class_variable_name,
            counter=0,
        )
        previous_values = []
        statements = [ResetStatement(), class_declaration_statement]
        counter = 0
        for method_name in method_names:
            arguments = self.class_under_test_cu.get_arguments_of_public_method(
                method_name=method_name
            )
            input_statements = []
            for arg in arguments:
                input_qualified_class_name = ".".join(arg)
                input_class = ClassParser(
                    app_name=self.app_name,
                    qualified_class_name=input_qualified_class_name,
                )
                class_name = arg[-1]
                if input_class.is_interface():
                    interface_name = input_class.get_interface_name()
                    assert interface_name is not None, "Interface name is None"

                    qualified_interface_class_name = ".".join(
                        input_qualified_class_name.split(".")[:-1] + [interface_name]
                    )

                    classes_implementing_interface = find_classes_implementing_interface(
                        app_name=self.app_name,
                        qualified_interface_class_name=qualified_interface_class_name,
                    )

                    assert (
                        len(classes_implementing_interface) > 0
                    ), f"No classes implementing interface {interface_name} found"

                    selected_class = self.random_generator.rnd_state.choice(
                        classes_implementing_interface
                    )
                    class_name = selected_class.get_class_name()
                    assert class_name is not None, "Class name is None"

                    statement, value = self._handle_input_class(
                        input_class=selected_class,
                        class_name=class_name,
                        previous_values=previous_values,
                        counter=counter,
                    )
                else:
                    statement, value = self._handle_input_class(
                        input_class=input_class,
                        class_name=class_name,
                        previous_values=previous_values,
                        counter=counter,
                    )

                previous_values.append((class_name, value))

                input_statements.append(statement)
                statements.append(statement)
                counter += 1

            method_call_statement = MethodCallStatement(
                class_variable_name=class_declaration_statement.get_variable_name(),
                method_name=method_name,
                arguments=input_statements,
            )
            statements.append(method_call_statement)

        return statements

    @abstractmethod
    def get_state(self) -> Optional[GeneratorState]:
        raise NotImplementedError("Method get_state not implemented")

    @abstractmethod
    def set_state(self, generator_state: GeneratorState) -> None:
        raise NotImplementedError("Method set_state not implemented")

    @staticmethod
    def load_generator(
        generator_name: str,
        app_name: str,
        num_candidates: int,
        q: int,
        diversity_strategy: str,
    ) -> "TestCaseGenerator":

        assert app_name in APP_NAMES, f"App name {app_name} is not valid"
        assert (
            generator_name in GENERATOR_NAMES
        ), f"Generator name {generator_name} is not valid"

        assert os.path.exists(
            os.path.join(
                os.getcwd(), "generators", f"{generator_name}_test_case_generator.py"
            )
        ), f"Test case generator file not found: {generator_name}_test_case_generator.py"

        class_filename = Path(
            get_class_under_test_path(app_name=app_name, is_instrumented=True)
        ).name
        class_variable_name = class_filename.replace(".java", "")

        generator_module = importlib.import_module(
            f"generators.{generator_name}_test_case_generator"
        )
        for name, cls in generator_module.__dict__.items():
            if (
                name.lower()
                == f"{generator_name.capitalize()}TestCaseGenerator".lower()
                and issubclass(cls, TestCaseGenerator)
            ):
                if (
                    generator_name == DISTANCE_GENERATOR_NAME
                    or generator_name == LENGTH_GENERATOR_NAME
                ):
                    if generator_name == DISTANCE_GENERATOR_NAME:
                        return cls(
                            app_name=app_name,
                            class_variable_name=class_variable_name,
                            num_candidates=num_candidates,
                            diversity_strategy=diversity_strategy,
                        )
                    return cls(
                        app_name=app_name,
                        class_variable_name=class_variable_name,
                        num_candidates=num_candidates,
                    )
                if generator_name == QGRAMS_GENERATOR_NAME:
                    return cls(
                        app_name=app_name,
                        class_variable_name=class_variable_name,
                        num_candidates=num_candidates,
                        diversity_strategy=diversity_strategy,
                        q=q,
                    )
                return cls(app_name=app_name, class_variable_name=class_variable_name)
        raise ValueError(
            f"Test case generator class not found in generators.{generator_name}_test_case_generator.py"
        )


if __name__ == "__main__":
    test_suite = TestCaseGenerator.parse_final_test_suite(
        test_suite_filepath=os.path.join(
            "results", DIMESHIFT_NAME, "qgrams", "2024-07-21_01-38-09_0_test_suite.txt"
        )
    )
    print(test_suite[0].to_string())
