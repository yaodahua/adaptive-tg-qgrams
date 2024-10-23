import os
from typing import List

from config import APP_NAMES
from statements.method_call_statement import MethodCallStatement
from statements.statement import Statement

HELPER_FUNCTION_NAME = "runWithExceptionHandling"


def get_graph_path(app_name: str, check_existance: bool = True) -> str:

    assert app_name in APP_NAMES, f"App name {app_name} is not valid"

    graph_path = os.path.join(os.getcwd(), "graphs", f"{app_name}.txt")
    if check_existance:
        assert os.path.exists(graph_path), f"Graph file {graph_path} does not exist"
    return graph_path


def get_project_path(app_name: str, check_existance: bool = True) -> str:

    assert app_name in APP_NAMES, f"App name {app_name} is not valid"

    project_path = os.path.join(os.getcwd(), "apps", app_name, "src", "main", "java")
    if check_existance:
        assert os.path.exists(
            project_path
        ), f"Project path {project_path} does not exist"
    return project_path


def write_test_case_to_file(
    app_name: str, statements: List[Statement], statement_strings: List[str]
) -> None:

    assert app_name in APP_NAMES, f"App name {app_name} is not valid"

    main_cleaned_class_path = get_main_class_path(app_name=app_name, cleaned=True)

    code = []

    with open(main_cleaned_class_path, "r") as f:
        for line in f.readlines():

            if "public class MainClean" in line:
                code.append("public class Main {")
            else:
                code.append(line.replace("\n", ""))

            if "public static void main(String[] args)" in line:
                for i, statement_string in enumerate(statement_strings):
                    if isinstance(statements[i], MethodCallStatement):
                        statement_string = statement_string.replace(";", "")
                        code.append(
                            "        "
                            + f"{HELPER_FUNCTION_NAME}(() -> {statement_string});"
                        )
                    else:
                        code.append("        " + statement_string)

    main_class_path = get_main_class_path(
        app_name=app_name, cleaned=False, check_existance=False
    )

    with open(main_class_path, "w") as f:
        for line in code:
            f.write(line + "\n")


def get_main_package_qualified_class_name(cleaned: bool = False) -> str:
    if cleaned:
        return "main.MainClean"
    return "main.Main"


def get_main_class_path(
    app_name: str, cleaned: bool = False, check_existance: bool = True
) -> str:

    assert app_name in APP_NAMES, f"App name {app_name} is not valid"

    main_class_qualified_name = get_main_package_qualified_class_name(cleaned=cleaned)
    project_path = get_project_path(app_name=app_name)
    package_name = main_class_qualified_name.split(".")[0]
    class_name = main_class_qualified_name.split(".")[1]

    class_path = os.path.join(project_path, package_name, class_name + ".java")

    if check_existance:
        assert os.path.exists(
            class_path
        ), f"Class {main_class_qualified_name} does not exist in the project"

    return class_path


def get_class_under_test_path(
    app_name: str, check_existance: bool = True, is_instrumented: bool = False
) -> str:

    assert app_name in APP_NAMES, f"App name {app_name} is not valid"

    if is_instrumented:
        filename = "ClassUnderTestInstr.java"
    else:
        filename = "ClassUnderTest.java"
    src_file = os.path.join(
        os.getcwd(),
        "apps",
        app_name,
        "src",
        "main",
        "java",
        "main",
    )
    if check_existance:
        assert os.path.exists(src_file), f"Source file {src_file} does not exist"
        assert os.path.exists(
            os.path.join(src_file, filename)
        ), f"File {filename} does not exist"
    return os.path.join(src_file, filename)


def get_instrumented_class_file(app_name: str) -> str:

    assert app_name in APP_NAMES, f"App name {app_name} is not valid"

    class_file = os.path.join(
        os.getcwd(),
        "apps",
        app_name,
        "target",
        "classes",
        "main",
        "ClassUnderTestInstr.class",
    )
    return class_file


def get_coverage_targets_file(app_name: str) -> str:

    assert app_name in APP_NAMES, f"App name {app_name} is not valid"

    coverage_targets_file = os.path.join(
        os.getcwd(),
        "apps",
        app_name,
        "coverage_targets.pkl",
    )
    return coverage_targets_file
