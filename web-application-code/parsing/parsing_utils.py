from typing import List
from config import APP_NAMES
from parsing.class_parser import ClassParser
from utils.file_utils import get_project_path
import os


def find_classes_implementing_interface(
    app_name: str, qualified_interface_class_name: str
) -> List[ClassParser]:

    assert app_name in APP_NAMES, f"App name {app_name} is not valid"

    result = []

    project_path = get_project_path(app_name=app_name)
    interface_name = qualified_interface_class_name.split(".")[-1]
    package_name = qualified_interface_class_name.split(".")[0]

    # assuming the interface is in the same package as the classes

    for class_name in os.listdir(os.path.join(project_path, package_name)):
        qualified_class_name = f"{package_name}.{class_name.split('.')[0]}"
        class_parser = ClassParser(
            app_name=app_name, qualified_class_name=qualified_class_name
        )
        if class_parser.implements_interface(interface_name=interface_name):
            result.append(class_parser)

    return result
