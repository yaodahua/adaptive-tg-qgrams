import re
from statements.statement import Statement
from statements.variable_declaration import VariableDeclaration


class EnumStatement(VariableDeclaration, Statement):

    def __init__(self, class_name: str, value: str, counter: int) -> None:
        super().__init__(class_name=class_name, counter=counter)
        self.value = value

    def clone(self) -> "EnumStatement":
        return EnumStatement(
            class_name=self.class_name, value=self.value, counter=self.counter
        )

    def to_string(self) -> str:
        return f"{self.class_name} {self.get_variable_name()} = {self.class_name}.{self.value};"

    def __eq__(self, other: "EnumStatement") -> bool:
        return super().__eq__(other=other)

    @staticmethod
    def from_string(statement_string: str) -> "EnumStatement":
        if re.search(r"= \w+\.\w+;", statement_string) is not None:
            parts = statement_string.split()
            class_name = parts[0]
            variable_name = parts[1]
            counter = VariableDeclaration.parse_counter_in_variable_name(
                variable_name=variable_name
            )
            assert (
                len(parts[3].split(".")) > 1
            ), f"Invalid enum statement: {statement_string}"
            value = parts[3].split(".")[1].replace(";", "")

            return EnumStatement(class_name=class_name, counter=counter, value=value)
        raise ValueError(f"Unknown statement: {statement_string}")
