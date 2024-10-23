import os
from typing import List
import javalang
import pickle

from config import (
    APP_NAMES,
    SPLITTYPIE_NAME,
)
from executors.coverage_target import CoverageTarget
from global_log import GlobalLog
from parsing import unparse_utils
from utils.file_utils import (
    get_class_under_test_path,
    get_coverage_targets_file,
    get_instrumented_class_file,
)


class Instrument:

    def __init__(self, app_name: str) -> None:

        assert app_name in APP_NAMES, f"App name {app_name} is not valid"

        lines = []
        self.app_name = app_name
        self.cut_path = get_class_under_test_path(
            app_name=app_name, is_instrumented=False
        )
        with open(self.cut_path, "r") as f:
            lines = [line for line in f.readlines()]
            code = "".join(lines)

        self.tree = javalang.parse.parse(code)
        self.logger = GlobalLog(logger_prefix="Instrument")

    def needs_instrumentation(self) -> bool:
        class_file = get_instrumented_class_file(app_name=self.app_name)
        return not os.path.exists(class_file)

    @staticmethod
    def _instrument_block_statement(
        block_statement: javalang.tree.BlockStatement, method_name: str
    ) -> List[CoverageTarget]:
        block_statement.statements.insert(
            0,
            javalang.tree.StatementExpression(
                expression=javalang.tree.MethodInvocation(
                    member="logger.log",
                    arguments=[
                        javalang.tree.Literal(value="Level.INFO"),
                        javalang.tree.Literal(
                            value=f'"IF-{block_statement.position.line}"'
                        ),
                    ],
                )
            ),
        )
        return CoverageTarget(
            target_type="IF",
            line_number=block_statement.position.line,
            method_name=method_name,
        )

    def add_probes_and_get_coverage_targets(self) -> List[CoverageTarget]:
        self.logger.debug(f"Adding probes to the code {self.cut_path}")

        coverage_targets = []
        current_method_name = None
        current_block_statement = None
        nodes_to_instrument = dict()

        # Traverse the AST and modify it
        for _, node in self.tree:
            if isinstance(node, javalang.tree.CompilationUnit):
                node.imports.insert(
                    1, javalang.tree.Import(path="java.util.logging.Level")
                )
                node.imports.insert(
                    2, javalang.tree.Import(path="java.util.logging.Logger")
                )

            elif isinstance(node, javalang.tree.ClassDeclaration):
                node.body.insert(
                    1,
                    javalang.tree.FieldDeclaration(
                        modifiers=["private", "final", "static"],
                        type=javalang.tree.ReferenceType(arguments=None, name="Logger"),
                        declarators=[
                            javalang.tree.VariableDeclarator(
                                name="logger",
                                initializer=javalang.tree.MethodInvocation(
                                    member="Logger.getLogger",
                                    arguments=[
                                        javalang.tree.Literal(
                                            value=node.name + "Instr.class.getName()"
                                        )
                                    ],
                                ),
                            )
                        ],
                    ),
                )
                node.name += "Instr"

            elif isinstance(node, javalang.tree.ConstructorDeclaration):
                node.name += "Instr"

            elif isinstance(node, javalang.tree.MethodDeclaration):
                current_method_name = node.name

            elif isinstance(node, javalang.tree.BlockStatement):
                current_block_statement = node

            elif isinstance(node, javalang.tree.StatementExpression):
                if (
                    isinstance(node.expression, javalang.tree.Assignment)
                    and isinstance(node.expression.expressionl, javalang.tree.This)
                    and len(node.expression.expressionl.selectors) > 0
                    and isinstance(
                        node.expression.expressionl.selectors[0],
                        javalang.tree.MemberReference,
                    )
                    and node.expression.expressionl.selectors[0].member == "currentPage"
                ):
                    if current_method_name is not None:
                        if current_method_name not in nodes_to_instrument:
                            nodes_to_instrument[current_method_name] = []

                        nodes_to_instrument[current_method_name].append(
                            (node, current_block_statement)
                        )

        for method_name, nodes_with_block_statement in nodes_to_instrument.items():
            for node, block_statement in nodes_with_block_statement:
                coverage_targets.append(
                    self._instrument_block_statement(
                        block_statement=block_statement, method_name=method_name
                    )
                )

        modified_code = unparse_utils.unparse(node=self.tree)

        cut_instrumented_path = get_class_under_test_path(
            app_name=self.app_name, check_existance=False, is_instrumented=True
        )
        self.logger.debug(f"Saving instrumented file {cut_instrumented_path}")
        with open(cut_instrumented_path, "w") as f:
            f.write(modified_code)

        coverage_targets_filepath = get_coverage_targets_file(app_name=self.app_name)

        with open(coverage_targets_filepath, "wb") as f:
            pickle.dump(coverage_targets, f)

        return coverage_targets


if __name__ == "__main__":

    coverage_targets = Instrument(
        app_name=SPLITTYPIE_NAME
    ).add_probes_and_get_coverage_targets()
    print(len(coverage_targets))
