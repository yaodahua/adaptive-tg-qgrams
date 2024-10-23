import re
from typing import List
from statements.statement import Statement
from statements.variable_declaration import VariableDeclaration


class MethodCallStatement(Statement):

    def __init__(
        self,
        class_variable_name: str,
        method_name: str,
        arguments: List[VariableDeclaration],
    ) -> None:
        super().__init__()
        self.class_variable_name = class_variable_name
        self.arguments = arguments
        self.args_string = ", ".join(
            [argument.get_variable_name() for argument in self.arguments]
        )
        self.method_name = (
            method_name.split("(")[0] if "(" in method_name else method_name
        )

    def clone(self) -> "MethodCallStatement":
        return MethodCallStatement(
            class_variable_name=self.class_variable_name,
            method_name=self.method_name,
            arguments=[argument.clone() for argument in self.arguments],
        )

    def to_string(self) -> str:
        return f"{self.class_variable_name}.{self.method_name}({self.args_string});"

    # for distance computation it stays this way, i.e., without comparing the arguments
    def __eq__(self, other: "MethodCallStatement") -> bool:
        if isinstance(other, MethodCallStatement):
            return self.method_name == other.method_name
        return False

    @staticmethod
    def from_string(statement_string) -> str:
        if re.search(r"\w+\.\w+\(.*\);", statement_string) is not None:
            parts = statement_string.split(".")
            class_variable_name = parts[0]
            method_name = re.search(r"\w+", parts[1]).group(0)
            args_string = re.search(r"\((.*?)\)", parts[1]).group(0)
            arguments = []
            if args_string == "()":
                return MethodCallStatement(
                    class_variable_name=class_variable_name,
                    method_name=method_name,
                    arguments=arguments,
                )
            if len(args_string.split(",")) > 1:
                args_parts = args_string.split(", ")
                for args_part in args_parts:
                    args_part = args_part.replace(")", "").replace("(", "")
                    arguments.append(
                        VariableDeclaration.from_string(variable_string=args_part)
                    )
            else:
                args_string = args_string.replace("(", "").replace(")", "")
                arguments.append(
                    VariableDeclaration.from_string(variable_string=args_string)
                )
            return MethodCallStatement(
                class_variable_name=class_variable_name,
                method_name=method_name,
                arguments=arguments,
            )
