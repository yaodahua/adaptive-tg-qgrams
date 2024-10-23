from typing import List, Optional, Tuple
import javalang
import os

import javalang.tree

from config import APP_NAMES, DIMESHIFT_NAME
from global_log import GlobalLog
from utils.file_utils import get_class_under_test_path, get_project_path


class ClassParser:

    def __init__(self, app_name: str, qualified_class_name: str = None):

        assert app_name in APP_NAMES, f"App name {app_name} is not valid"

        if qualified_class_name is None:
            self.class_path = get_class_under_test_path(
                app_name=app_name, is_instrumented=False
            )
        else:
            assert not qualified_class_name.endswith(
                ".java"
            ), "Class name should not end with .java"
            assert "." in qualified_class_name, "Class name should be qualified"

            project_path = get_project_path(app_name=app_name)
            package_name = qualified_class_name.split(".")[0]
            class_name = qualified_class_name.split(".")[1]

            self.class_path = os.path.join(
                project_path, package_name, class_name + ".java"
            )

            assert os.path.exists(
                self.class_path
            ), f"Class {qualified_class_name} does not exist in the project"

        with open(self.class_path, "r") as f:
            lines = [line for line in f.readlines()]
            code = "".join(lines)

        self.tree = javalang.parse.parse(code)
        self.logger = GlobalLog(logger_prefix="ClassParser")

        self.cached_methods = dict()

    def get_public_method_names(self) -> List[javalang.tree.MethodDeclaration]:
        return [method.name for method in self._get_public_methods()]

    def _get_public_methods(self) -> List[javalang.tree.MethodDeclaration]:
        public_methods = []

        for _, node in self.tree.filter(javalang.tree.MethodDeclaration):
            if "public" in node.modifiers:
                public_methods.append(node)

        return public_methods

    def get_arguments_of_public_method(self, method_name: str) -> List[Tuple[str]]:
        arguments = []

        if method_name in self.cached_methods:
            method = self.cached_methods[method_name]
        else:
            methods = list(
                filter(
                    lambda node: node.name == method_name, self._get_public_methods()
                )
            )
            assert (
                len(methods) == 1
            ), f"Method {method_name} does not exist in the class"

            method = methods[0]

            if method_name not in self.cached_methods:
                self.cached_methods[method_name] = method

        for parameter in method.parameters:
            if isinstance(parameter, javalang.tree.FormalParameter):
                if getattr(parameter.type, "sub_type", None) is not None:
                    arguments.append(
                        (parameter.type.name, parameter.type.sub_type.name)
                    )
                else:
                    arguments.append((parameter.type.name))
            else:
                raise RuntimeError(f"Unknown parameter type {type(parameter)}")

        return arguments

    def get_enum_values(self) -> List[str]:
        return [
            node.name
            for _, node in self.tree.filter(javalang.tree.EnumConstantDeclaration)
        ]

    def is_interface(self) -> bool:
        for _, node in self.tree.filter(javalang.tree.InterfaceDeclaration):
            return True
        return False

    def get_class_name(self) -> Optional[str]:
        for _, node in self.tree.filter(javalang.tree.ClassDeclaration):
            return node.name
        for _, node in self.tree.filter(javalang.tree.EnumDeclaration):
            return node.name

    def get_interface_name(self) -> Optional[str]:
        assert self.is_interface(), "Class is not an interface"
        for _, node in self.tree.filter(javalang.tree.InterfaceDeclaration):
            return node.name

    def implements_interface(self, interface_name: str) -> bool:
        for _, node in self.tree.filter(javalang.tree.ClassDeclaration):
            for interface in node.implements:
                if interface.name == interface_name:
                    return True

        for _, node in self.tree.filter(javalang.tree.EnumDeclaration):
            for interface in node.implements:
                if interface.name == interface_name:
                    return True

        return False

    def is_range_type(self) -> bool:
        for _, node in self.tree.filter(javalang.tree.ClassDeclaration):
            if getattr(node, "extends", None) is not None:
                return node.extends.name == "Range"
        return False

    def get_intervals_for_range_type(self) -> List[int]:
        assert self.is_range_type(), "Class is not a range type"
        field_declarations = [
            node for _, node in self.tree.filter(javalang.tree.FieldDeclaration)
        ]
        assert len(field_declarations) >= 2, "Expected at least two field declarations"
        field_declaration_lowers = list(
            filter(
                lambda x: getattr(x, "declarators", None)
                and x.declarators[0].name == "lower",
                field_declarations,
            )
        )
        assert (
            len(field_declaration_lowers) == 1
        ), "Expected one field declaration named 'lower'"
        field_declaration_lower = field_declaration_lowers[0]
        field_declaration_uppers = list(
            filter(
                lambda x: getattr(x, "declarators", None)
                and x.declarators[0].name == "upper",
                field_declarations,
            )
        )
        assert (
            len(field_declaration_uppers) == 1
        ), "Expected one field declaration named 'upper'"
        field_declaration_upper = field_declaration_uppers[0]
        assert (
            field_declaration_lower.type.name == "int"
            and field_declaration_upper.type.name == "int"
        ), "Expected int fields"
        lower_value = int(field_declaration_lower.declarators[0].initializer.value)
        upper_value = int(field_declaration_upper.declarators[0].initializer.value)
        return [lower_value, upper_value]


if __name__ == "__main__":
    class_parser = ClassParser(
        app_name=DIMESHIFT_NAME, qualified_class_name="custom_classes.Amount"
    )
