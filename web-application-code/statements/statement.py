from abc import ABC, abstractmethod
import importlib

import re


class Statement(ABC):

    @abstractmethod
    def clone(self) -> "Statement":
        pass

    @abstractmethod
    def to_string(self) -> str:
        pass

    @staticmethod
    def from_string(statement_string: str) -> "Statement":
        # re.match checks for patterns at the beginning of the string
        # re.search checks for patterns anywhere in the string
        if statement_string.startswith("ResetAppState"):
            statement_module = importlib.import_module("statements.reset_statement")
            class_name = "ResetStatement"
        elif " new " in statement_string:
            statement_module = importlib.import_module(
                "statements.class_declaration_statement"
            )
            class_name = "ClassDeclarationStatement"
        elif re.search(r"= \w+\.\w+;", statement_string) is not None:
            statement_module = importlib.import_module("statements.enum_statement")
            class_name = "EnumStatement"
        elif re.search(r"\w+\.\w+\(.*\);", statement_string) is not None:
            statement_module = importlib.import_module(
                "statements.method_call_statement"
            )
            class_name = "MethodCallStatement"
        else:
            raise ValueError(f"Unknown statement type: {statement_string}")

        for name, cls in statement_module.__dict__.items():
            if name.lower() == class_name.lower() and issubclass(cls, Statement):
                return cls.from_string(statement_string=statement_string)
