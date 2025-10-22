"""
测试用例生成器抽象基类

本文件定义了测试用例生成器的抽象基类 TestCaseGenerator, 为各种测试生成策略提供统一接口.
主要功能包括:
1. 测试用例生成: 基于图解析和随机游走生成测试用例
2. 测试套件管理: 存储, 更新和写入测试套件
3. 输入参数处理: 支持枚举类型和范围类型的参数生成
4. 方法调用构建: 构建完整的方法调用序列
5. 生成器加载: 动态加载不同类型的测试用例生成器

支持的生成器类型: Q-grams, SimIDF, TFIDF, 距离, 长度, 随机等
"""

from abc import ABC, abstractmethod
import importlib
import os
from pathlib import Path
from typing import List, Optional, Tuple, Union
from config import (
    APP_NAMES,
    DIMESHIFT_NAME,
    DISTANCE_GENERATOR_NAME,
    GENERATOR_NAMES,
    LENGTH_GENERATOR_NAME,
    QGRAMS_GENERATOR_NAME,
    SIMIDF_GENERATOR_NAME,
    TFIDF_GENERATOR_NAME,
)
from executors.coverage_target import CoverageTarget
from global_log import GlobalLog
from individuals.individual import Individual
from parsing.class_parser import ClassParser
from parsing.graph_parser import GraphParser
from parsing.parsing_utils import find_classes_implementing_interface
from statements.class_declaration_statement import ClassDeclarationStatement
from statements.enum_statement import EnumStatement
from statements.method_call_statement import MethodCallStatement
from statements.reset_statement import ResetStatement
from statements.statement import Statement
from type_aliases import GeneratorState
from utils.file_utils import get_class_under_test_path, get_graph_path
from utils.randomness_utils import RandomGenerator


class TestCaseGenerator(ABC):
    """测试用例生成器抽象基类"""

    def __init__(self, app_name: str, class_variable_name: str):
        """初始化测试用例生成器
        
        参数:
            app_name: 应用程序名称
            class_variable_name: 类变量名称
        """
        assert app_name in APP_NAMES, f"App name {app_name} is not valid"

        self.app_name = app_name  # 应用程序名称
        self.class_variable_name = class_variable_name  # 类变量名称
        self.graph_parser = GraphParser(  # 图解析器, 用于解析方法调用图
            graph_dot_file=get_graph_path(app_name=app_name)
        )
        self.logger = GlobalLog(logger_prefix="TestCaseGenerator")  # 日志记录器
        self.class_under_test_cu = ClassParser(app_name=app_name)  # 被测试类解析器
        self.random_generator = RandomGenerator.get_instance()  # 随机数生成器
        self.executed_individuals: List[Individual] = []  # 已执行的测试用例列表
        self.final_test_suite: List[Tuple[Individual, List[CoverageTarget]]] = []  # 最终测试套件

    def store_executed_individual(self, individual: Individual) -> None:
        """存储已执行的测试用例"""
        self.executed_individuals.append(individual)

    def get_final_test_suite(self) -> List[Tuple[Individual, List[CoverageTarget]]]:
        """获取最终测试套件"""
        return self.final_test_suite

    def set_final_test_suite(
        self, final_test_suite: List[Tuple[Individual, List[CoverageTarget]]]
    ) -> None:
        """设置最终测试套件"""
        self.final_test_suite = [
            (individual.clone(), [ct.clone() for ct in coverage_targets])
            for individual, coverage_targets in final_test_suite
        ]

    def update_final_test_suite(
        self, individual: Individual, covered_targets: List[CoverageTarget]
    ) -> None:
        """更新最终测试套件, 添加新的测试用例和覆盖目标"""
        new_individual = individual.clone()
        new_individual.statements = Individual.remove_dangling_statements(
            statements=individual.statements
        )
        self.final_test_suite.append((new_individual, covered_targets))

    @staticmethod
    def parse_final_test_suite(test_suite_filepath: str) -> List[Individual]:
        """从文件解析最终测试套件
        
        参数:
            test_suite_filepath: 测试套件文件路径
        
        返回:
            解析后的测试用例列表
        """
        with open(test_suite_filepath, "r") as f:
            lines = f.readlines()

        individuals_strings = dict()  # 存储每个测试用例的字符串
        count = 0
        for line in lines:
            if line.startswith("/*") or line.startswith("*"):  # 跳过注释行
                if line.startswith("****"):  # 测试用例分隔符
                    count += 1
                continue

            if str(count) not in individuals_strings:  # 初始化测试用例字符串列表
                individuals_strings[str(count)] = []

            individuals_strings[str(count)].append(line.strip())  # 存储测试用例字符串

        return [
            Individual.parse_statement_strings(statement_strings=individual_string)
            for individual_string in individuals_strings.values()
        ]

    def write_final_test_suite(
        self, covered_targets: List[CoverageTarget]
    ) -> List[str]:
        """写入最终测试套件到字符串格式
        
        参数:
            covered_targets: 已覆盖的目标列表
        
        返回:
            测试套件的字符串表示
        """
        assert len(self.final_test_suite) > 0, "Final test suite is empty"
        # 按覆盖目标数量排序测试用例
        sorted_test_suite = sorted(
            self.final_test_suite, key=lambda x: len(set(x[1])), reverse=True
        )
        i = 0
        covered_targets_local = set()  # 本地已覆盖目标集合
        minimized_test_suite: List[Individual] = []  # 最小化测试套件
        # 构建最小化测试套件, 确保覆盖所有目标
        while len(covered_targets_local) < len(covered_targets):
            current_coverage_targets = sorted_test_suite[i][1]
            if any(
                filter(
                    lambda x: x not in covered_targets_local, current_coverage_targets
                )
            ):
                self.logger.info(
                    f"Adding test case with id {sorted_test_suite[i][0].id} with # unique targets "
                    f"covered {len(set(current_coverage_targets))}"
                )
                minimized_test_suite.append(sorted_test_suite[i])
                covered_targets_local.update(current_coverage_targets)
                self.logger.info(
                    f"Total targets covered: {len(covered_targets_local)}/{len(covered_targets)}"
                )
            i += 1

        all_strings = []
        for individual, coverage_targets in minimized_test_suite:
            all_strings.append("/*")  # 开始注释块
            for ct in coverage_targets:
                all_strings.append(f"* {ct.__str__()}")  # 添加覆盖目标信息
            all_strings.append("*/")  # 结束注释块
            all_strings.append("\n".join(individual.to_string()))  # 测试用例内容
            all_strings.append("*" * 20)  # 分隔符

        return "\n".join(all_strings)

    @abstractmethod
    def generate(
        self, uncovered_targets: List[CoverageTarget], max_length: int
    ) -> Individual:
        """抽象方法: 生成测试用例
        
        参数:
            uncovered_targets: 未覆盖的目标列表
            max_length: 测试用例最大长度
        
        返回:
            生成的测试用例
        """
        pass
    
    def generate_individual(
        self, target_edge_name: str, max_length: int = 30
    ) -> Individual:
        """生成单个测试用例
        
        参数:
            target_edge_name: 目标边的名称
            max_length: 随机测试用例的最大长度, 默认30
        
        返回:
            生成的测试用例个体
        """
        # 从索引到目标边的随机游走
        random_walk = self.graph_parser.get_random_walk_from_index_to_target_edge(
            target_edge_name=target_edge_name, max_length=max_length 
        )
        # 路径验证: 确保随机游走不为空, 且最后一个节点是目标边
        assert len(random_walk) > 0, "Random walk should not be empty"
        assert (
            target_edge_name in random_walk[-1]
        ), f"Random walk should end at target edge: {target_edge_name} != {random_walk[-1]}, len(random_walk)={len(random_walk)}"
        
        # 语句构建: 将随机游走中的方法调用转换为语句
        statements = self.build_method_calls(method_names=random_walk)
        return Individual(statements=statements)

    def _handle_input_class(
        self,
        input_class: ClassParser,
        class_name: str,
        previous_values: List[Tuple[str, Union[int, str]]],
        counter: int,
    ) -> Tuple[Statement, Union[int, str]]:
        """处理输入类, 生成对应的语句和值
        
        参数:
            input_class: 输入类解析器
            class_name: 类名称
            previous_values: 之前生成的值列表
            counter: 计数器
        
        返回:
            生成的语句和对应的值
        """
        value = None
        # 获取可用的先前值
        usable_previous_values = list(
            map(
                lambda x: x[1],
                filter(lambda x: x[0] == class_name, previous_values),
            )
        )

        if len(input_class.get_enum_values()) > 0:  # 枚举类型处理
            # 50%概率重用之前的值, 否则随机选择新值
            if (
                self.random_generator.rnd_state.rand() < 0.5
                and len(usable_previous_values) > 0
            ):
                enum_value = self.random_generator.rnd_state.choice(
                    usable_previous_values
                )
            else:
                enum_value = self.random_generator.rnd_state.choice(
                    input_class.get_enum_values()
                )
            statement = EnumStatement(
                class_name=class_name,
                value=enum_value,
                counter=counter,
            )
            value = enum_value

        elif input_class.is_range_type():  # 范围类型处理
            # 50%概率重用之前的值, 否则随机生成新值
            if (
                self.random_generator.rnd_state.rand() < 0.5
                and len(usable_previous_values) > 0
            ):
                range_value = self.random_generator.rnd_state.choice(
                    usable_previous_values
                )
            else:
                intervals = input_class.get_intervals_for_range_type()
                range_value = self.random_generator.rnd_state.randint(
                    low=intervals[0] - 1, high=intervals[1] + 1
                )

            statement = ClassDeclarationStatement(
                class_name=class_name, value=range_value, counter=counter
            )
            value = range_value

        else:
            raise NotImplementedError(
                f"Input class {class_name} is not an enum nor a range"
            )

        return statement, value

    def build_method_calls(self, method_names: List[str]) -> List[Statement]:
        """构建方法调用序列
        
        参数:
            method_names: 方法名称列表
        
        返回:
            构建的语句列表
        """
        # 创建类声明语句
        class_declaration_statement = ClassDeclarationStatement(
            class_name=self.class_variable_name,
            counter=0,
        )
        previous_values = []  # 存储之前生成的值
        statements = [ResetStatement(), class_declaration_statement]  # 初始语句
        counter = 0
        
        # 遍历每个方法名
        for method_name in method_names:
            # 获取方法的参数信息
            arguments = self.class_under_test_cu.get_arguments_of_public_method(
                method_name=method_name
            )
            input_statements = []  # 输入参数语句
            
            # 处理每个参数
            for arg in arguments:
                input_qualified_class_name = ".".join(arg)
                input_class = ClassParser(
                    app_name=self.app_name,
                    qualified_class_name=input_qualified_class_name,
                )
                class_name = arg[-1]
                
                if input_class.is_interface():  # 接口类型处理
                    interface_name = input_class.get_interface_name()
                    assert interface_name is not None, "Interface name is None"

                    qualified_interface_class_name = ".".join(
                        input_qualified_class_name.split(".")[:-1] + [interface_name]
                    )

                    # 查找实现该接口的类
                    classes_implementing_interface = find_classes_implementing_interface(
                        app_name=self.app_name,
                        qualified_interface_class_name=qualified_interface_class_name,
                    )

                    assert (
                        len(classes_implementing_interface) > 0
                    ), f"No classes implementing interface {interface_name} found"

                    # 随机选择一个实现类
                    selected_class = self.random_generator.rnd_state.choice(
                        classes_implementing_interface
                    )
                    class_name = selected_class.get_class_name()
                    assert class_name is not None, "Class name is None"

                    statement, value = self._handle_input_class(
                        input_class=selected_class,
                        class_name=class_name,
                        previous_values=previous_values,
                        counter=counter,
                    )
                else:  # 普通类处理
                    statement, value = self._handle_input_class(
                        input_class=input_class,
                        class_name=class_name,
                        previous_values=previous_values,
                        counter=counter,
                    )

                previous_values.append((class_name, value))
                input_statements.append(statement)
                statements.append(statement)
                counter += 1

            # 创建方法调用语句
            method_call_statement = MethodCallStatement(
                class_variable_name=class_declaration_statement.get_variable_name(),
                method_name=method_name,
                arguments=input_statements,
            )
            statements.append(method_call_statement)

        return statements

    @abstractmethod
    def get_state(self) -> Optional[GeneratorState]:
        """抽象方法: 获取生成器状态"""
        raise NotImplementedError("Method get_state not implemented")

    @abstractmethod
    def set_state(self, generator_state: GeneratorState) -> None:
        """抽象方法: 设置生成器状态"""
        raise NotImplementedError("Method set_state not implemented")

    @staticmethod
    def load_generator(
        generator_name: str,
        app_name: str,
        num_candidates: int,
        q: int,
        diversity_strategy: str,
    ) -> "TestCaseGenerator":
        """静态方法: 加载指定类型的测试用例生成器
        
        参数:
            generator_name: 生成器名称
            app_name: 应用程序名称
            num_candidates: 候选测试用例数量
            q: Q-grams参数
            diversity_strategy: 多样性策略
        
        返回:
            加载的测试用例生成器实例
        """
        assert app_name in APP_NAMES, f"App name {app_name} is not valid"
        assert (
            generator_name in GENERATOR_NAMES
        ), f"Generator name {generator_name} is not valid"

        # 检查生成器文件是否存在
        assert os.path.exists(
            os.path.join(
                os.getcwd(), "generators", f"{generator_name}_test_case_generator.py"
            )
        ), f"Test case generator file not found: {generator_name}_test_case_generator.py"

        # 获取类变量名称
        class_filename = Path(
            get_class_under_test_path(app_name=app_name, is_instrumented=True)
        ).name
        class_variable_name = class_filename.replace(".java", "")

        # 动态导入生成器模块
        generator_module = importlib.import_module(
            f"generators.{generator_name}_test_case_generator"
        )
        
        # 查找生成器类
        for name, cls in generator_module.__dict__.items():
            if (
                name.lower()
                == f"{generator_name.capitalize()}TestCaseGenerator".lower()
                and issubclass(cls, TestCaseGenerator)
            ):
                # 根据生成器类型创建相应实例
                if (
                    generator_name == DISTANCE_GENERATOR_NAME
                    or generator_name == LENGTH_GENERATOR_NAME
                ):
                    if generator_name == DISTANCE_GENERATOR_NAME:
                        return cls(
                            app_name=app_name,
                            class_variable_name=class_variable_name,
                            num_candidates=num_candidates,
                            diversity_strategy=diversity_strategy,
                        )
                    return cls(
                        app_name=app_name,
                        class_variable_name=class_variable_name,
                        num_candidates=num_candidates,
                    )
                if generator_name == QGRAMS_GENERATOR_NAME:
                    return cls(
                        app_name=app_name,
                        class_variable_name=class_variable_name,
                        num_candidates=num_candidates,
                        diversity_strategy=diversity_strategy,
                        q=q,
                    )
                if generator_name == SIMIDF_GENERATOR_NAME:
                    return cls(
                        app_name=app_name,
                        class_variable_name=class_variable_name,
                        num_candidates=num_candidates,
                        diversity_strategy=diversity_strategy,
                    )
                if generator_name == TFIDF_GENERATOR_NAME:
                    return cls(
                        app_name=app_name,
                        class_variable_name=class_variable_name,
                        num_candidates=num_candidates,
                        diversity_strategy=diversity_strategy,
                        q=q,
                    )
                return cls(app_name=app_name, class_variable_name=class_variable_name)
        raise ValueError(
            f"Test case generator class not found in generators.{generator_name}_test_case_generator.py"
        )


if __name__ == "__main__":
    test_suite = TestCaseGenerator.parse_final_test_suite(
        test_suite_filepath=os.path.join(
            "results", DIMESHIFT_NAME, "qgrams", "2024-07-21_01-38-09_0_test_suite.txt"
        )
    )
    print(test_suite[0].to_string())
