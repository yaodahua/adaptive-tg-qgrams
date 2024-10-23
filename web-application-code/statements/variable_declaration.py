from abc import ABC
import re


class VariableDeclaration(ABC):

    def __init__(self, class_name: str, counter: int) -> None:
        self.class_name = class_name
        self.counter = counter

    def clone(self) -> "VariableDeclaration":
        return VariableDeclaration(class_name=self.class_name, counter=self.counter)

    def __eq__(self, other: "VariableDeclaration") -> bool:
        if isinstance(other, VariableDeclaration):
            return self.class_name == other.class_name and self.counter == other.counter
        return False

    def get_variable_name(self) -> str:
        return f"{self.class_name[0].lower() + self.class_name[1:]}{self.counter}"

    @staticmethod
    def parse_counter_in_variable_name(variable_name: str) -> int:
        try:
            counter = int(re.search(r"\d+", variable_name).group())
            return counter
        except ValueError:
            raise RuntimeError(
                f"Variable name {variable_name} does not contain a number"
            )

    @staticmethod
    def from_string(variable_string: str) -> "VariableDeclaration":
        counter = VariableDeclaration.parse_counter_in_variable_name(
            variable_name=variable_string
        )
        class_name = (
            variable_string.replace(str(counter), "").capitalize()[0]
            + variable_string.replace(str(counter), "")[1:]
        )
        return VariableDeclaration(class_name=class_name, counter=counter)
