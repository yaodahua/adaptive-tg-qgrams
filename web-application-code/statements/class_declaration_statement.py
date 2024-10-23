import re
from statements.statement import Statement
from statements.variable_declaration import VariableDeclaration


class ClassDeclarationStatement(VariableDeclaration, Statement):

    def __init__(self, class_name: str, counter: int, value: int = None) -> None:
        super().__init__(class_name=class_name, counter=counter)
        self.value = value

    def clone(self) -> "ClassDeclarationStatement":
        return ClassDeclarationStatement(
            class_name=self.class_name, counter=self.counter, value=self.value
        )

    def to_string(self) -> str:
        if self.value is None:
            return f"{self.class_name} {self.get_variable_name()} = new {self.class_name}();"
        return f"{self.class_name} {self.get_variable_name()} = new {self.class_name}({self.value});"

    def __eq__(self, other: "ClassDeclarationStatement") -> bool:
        return super().__eq__(other=other)

    @staticmethod
    def from_string(statement_string: str) -> "ClassDeclarationStatement":
        if " new " in statement_string:
            parts = statement_string.split()
            class_name = parts[0]
            variable_name = parts[1]
            counter = VariableDeclaration.parse_counter_in_variable_name(
                variable_name=variable_name
            )
            value = re.search(r"\((.*?)\)", parts[4]).group()
            if value == "()":
                return ClassDeclarationStatement(class_name=class_name, counter=counter)

            try:
                value = int(value.replace("(", "").replace(")", ""))
            except ValueError:
                raise RuntimeError(f"Value {value} is not a number")

            return ClassDeclarationStatement(
                class_name=class_name, counter=counter, value=value
            )
        raise ValueError(f"Unknown statement: {statement_string}")
