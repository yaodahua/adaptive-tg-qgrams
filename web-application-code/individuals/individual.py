from typing import Dict, List, Tuple

import numpy as np

from config import INPUT_DIVERSITY_STRATEGY_NAME, SEQUENCE_DIVERSITY_STRATEGY_NAME
from individuals.id_generator import IdGenerator
from statements.class_declaration_statement import ClassDeclarationStatement
from statements.enum_statement import EnumStatement
from scipy.stats import entropy
from statements.method_call_statement import MethodCallStatement
from statements.statement import Statement
import edit_distance

from statements.variable_declaration import VariableDeclaration


class Individual:

    def __init__(self, statements: List[Statement], start_count: int = 0) -> None:
        self.statements = statements
        self.id = IdGenerator.get_instance(start_count=start_count).get_id()

    def to_string(self) -> List[str]:
        return [statement.to_string() for statement in self.statements]

    @staticmethod
    def parse_statement_strings(statement_strings: List[str]) -> "Individual":
        return Individual(
            statements=[
                Statement.from_string(statement_string)
                for statement_string in statement_strings
            ]
        )

    def clone(self) -> "Individual":
        individual = Individual(
            statements=[statement.clone() for statement in self.statements],
            start_count=0,
        )
        individual.id = self.id
        return individual

    @staticmethod
    def remove_dangling_statements(statements: List[Statement]) -> List[Statement]:
        filtered_statements = [statement.clone() for statement in statements]
        variable_declarations = list(
            filter(
                lambda x: isinstance(x, VariableDeclaration),
                statements,
            )
        )
        for variable_declaration in variable_declarations:
            if not any(
                filter(
                    lambda x: isinstance(x, MethodCallStatement)
                    and (
                        variable_declaration in [arg for arg in x.arguments]
                        or x.class_variable_name
                        == variable_declaration.get_variable_name()
                    ),
                    statements,
                )
            ):
                filtered_statements.remove(variable_declaration)
        return filtered_statements

    def distance(
        self,
        other: "Individual",
        diversity_strategy: str = SEQUENCE_DIVERSITY_STRATEGY_NAME,
    ) -> float:
        assert (
            diversity_strategy == SEQUENCE_DIVERSITY_STRATEGY_NAME
        ), "Only sequence strategy is supported"
        method_calls_1 = list(
            filter(lambda x: isinstance(x, MethodCallStatement), self.statements)
        )
        method_calls_2 = list(
            filter(lambda x: isinstance(x, MethodCallStatement), other.statements)
        )
        sm = edit_distance.SequenceMatcher(a=method_calls_1, b=method_calls_2)
        return sm.distance()

    @staticmethod
    def compute_qgrams(
        diversity_strategy: str,
        qgram_counts: Dict[Tuple[str], int],
        individual: "Individual",
        q: int = 2,
    ) -> Dict[Tuple[str], int]:

        if diversity_strategy == SEQUENCE_DIVERSITY_STRATEGY_NAME:
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
        elif diversity_strategy == INPUT_DIVERSITY_STRATEGY_NAME:
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
            raise RuntimeError(f"Unknown diversity strategy: {diversity_strategy}")

        qgram_counts_local = dict(qgram_counts)

        for i in range(len(method_strs) - q + 1):
            qgram = tuple(method_strs[i : i + q])
            if qgram not in qgram_counts_local:
                qgram_counts_local[qgram] = 0
            qgram_counts_local[qgram] += 1

        return qgram_counts_local


if __name__ == "__main__":

    statement_strings_1 = [
        "classUnderTestInstr0.goToFind();",
        "classUnderTestInstr0.goToIndex();",
    ]
    statement_strings_2 = [
        "Name name0 = Name.JOHN;",
        "classUnderTestInstr0.findOwner(name0);",
        "classUnderTestInstr0.goToIndex();",
    ]
    statement_strings_3 = [
        "classUnderTestInstr0.goToFind();",
        "Id id0 = new Id(1);",
        "classUnderTestInstr0.find(id0);",
        "classUnderTestInstr0.goToFind();",
        "Id id1 = new Id(2);",
        "classUnderTestInstr0.find(id1);",
    ]
    statements_1 = [
        Statement.from_string(statement_string=statement_string)
        for statement_string in statement_strings_1
    ]
    statements_2 = [
        Statement.from_string(statement_string=statement_string)
        for statement_string in statement_strings_2
    ]
    statements_3 = [
        Statement.from_string(statement_string=statement_string)
        for statement_string in statement_strings_3
    ]
    individual_1 = Individual(statements=statements_1)
    individual_2 = Individual(statements=statements_2)
    individual_3 = Individual(statements=statements_3)

    print("Distance")
    print(individual_1.distance(other=individual_2))
    print(individual_1.distance(other=individual_3))

    candidates = [individual_2, individual_3]

    print("Qgrams_s")
    qgram_counts = Individual.compute_qgrams(
        diversity_strategy=SEQUENCE_DIVERSITY_STRATEGY_NAME,
        qgram_counts={},
        individual=individual_1,
    )
    print(qgram_counts)
    entropies = []
    for c in candidates:

        qgram_counts_local = dict(qgram_counts)
        qgram_counts_local = Individual.compute_qgrams(
            diversity_strategy=SEQUENCE_DIVERSITY_STRATEGY_NAME,
            qgram_counts=qgram_counts_local,
            individual=c,
        )
        print(qgram_counts_local)

        entropies.append(entropy(list(qgram_counts_local.values()), base=2))

    index_max_entropy = np.argmax(entropies)
    print(entropies)
    selected_individual = candidates[index_max_entropy]
    print(index_max_entropy)

    print("Qgrams_s+i")
    qgram_counts = Individual.compute_qgrams(
        diversity_strategy=INPUT_DIVERSITY_STRATEGY_NAME,
        qgram_counts={},
        individual=individual_1,
    )
    print(qgram_counts)
    entropies = []
    for c in candidates:

        qgram_counts_local = dict(qgram_counts)
        qgram_counts_local = Individual.compute_qgrams(
            diversity_strategy=INPUT_DIVERSITY_STRATEGY_NAME,
            qgram_counts=qgram_counts_local,
            individual=c,
        )
        print(qgram_counts_local)

        entropies.append(entropy(list(qgram_counts_local.values()), base=2))

    index_max_entropy = np.argmax(entropies)
    print(entropies)
    selected_individual = candidates[index_max_entropy]
    print(index_max_entropy)
