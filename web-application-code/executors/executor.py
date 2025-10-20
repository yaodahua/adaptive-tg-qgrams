from abc import ABC, abstractmethod
from collections import deque
import importlib
import os
import string
import time
from typing import List, Optional
import docker
import docker.models.containers

from config import APP_NAMES, CHROME_CONTAINER_NAME, RUNTIME_CONTAINER_NAME
from executors.execution_output import ExecutionOutput
from global_log import GlobalLog
from individuals.individual import Individual
from utils.file_utils import write_test_case_to_file
from utils.randomness_utils import RandomGenerator


class Executor(ABC):
    # Docker容器管理和测试执行的抽象基类

    def __init__(self, app_name: str):
        # 初始化执行器
        assert app_name in APP_NAMES, f"App name {app_name} is not valid"

        self.client = docker.from_env()  # Docker客户端
        self.network_queue = deque()  # 网络队列
        self.app_name = app_name  # 应用名称
        self.logger = GlobalLog(logger_prefix="Executor")  # 日志记录器
        self.random_generator = RandomGenerator.get_instance()  # 随机数生成器
        # 生成随机字符串用于容器命名
        self.random_string = "".join(
            self.random_generator.rnd_state.choice(
                list(string.ascii_letters) + list(string.digits), size=(16,)
            )
        )

    def start_containers(self) -> str:
        # 启动所有相关容器

        # 防止同一应用的多个实验同时运行
        containers = self.client.containers.list(filters={"status": "running"})
        for container in containers:
            if self.app_name in container.name:
                raise RuntimeError(
                    f"Cannot run experiments for the same app, since a container with name {container.name} already exists"
                )

        # 创建网络名称
        network_name = f"mynetwork_{self.random_string}"

        self.logger.debug(f"Creating network {network_name}")
        try:
            # 创建Docker网络
            self.client.networks.create(network_name, driver="bridge")
        except docker.errors.APIError:
            raise RuntimeError(f"Network {network_name} already exists")

        # 定义容器名称
        container_names = [
            f"{CHROME_CONTAINER_NAME}_{self.random_string}",
            f"{self.app_name}_{self.random_string}",
            f"{RUNTIME_CONTAINER_NAME}_{self.random_string}",
        ]
        
        # 启动每个容器
        for container_name in container_names:
            try:
                existing_container = self.client.containers.get(container_name)
                if existing_container:
                    raise RuntimeError(f"Container {container_name} already exists")
            except docker.errors.NotFound:
                pass

            self.start_container_by_name(
                network_name=network_name, container_name=container_name
            )

        # 将网络和容器信息加入队列
        self.network_queue.append({network_name: container_names})

        return network_name

    def start_container_by_name(
        self,
        network_name: str,
        container_name: str,
        add_container_to_network: bool = False,
    ) -> None:
        # 按名称启动特定容器

        if CHROME_CONTAINER_NAME in container_name:
            # 启动Chrome容器
            self._start_chrome_container(
                network_name=network_name, container_name=container_name
            )
            # 等待容器健康状态
            container = self.client.containers.get(container_name)
            max_counter = 100
            while container.health != "healthy" and max_counter > 0:
                time.sleep(1)
                max_counter -= 1
                container.reload()
            if max_counter == 0:
                raise RuntimeError(f"Container {container_name} did not start in time")

        elif RUNTIME_CONTAINER_NAME in container_name:
            # 启动运行时容器
            self._start_runtime_container(
                network_name=network_name, container_name=container_name
            )
        elif self.app_name in container_name:
            # 启动应用容器 (抽象方法, 由子类实现)
            self._start_application_container(
                network_name=network_name, container_name=container_name
            )
        else:
            raise ValueError(f"Invalid container name: {container_name}")

        # 等待容器运行状态
        container = self.client.containers.get(container_name)
        max_counter = 100
        while container.status != "running" and max_counter > 0:
            time.sleep(1)
            max_counter -= 1
            container.reload()
        if max_counter == 0:
            raise RuntimeError(f"Container {container_name} did not start in time")

        # 如果指定, 将容器添加到网络队列
        if add_container_to_network:
            container_added = False
            for network_dict in self.network_queue:
                if network_name in network_dict:
                    container_names = network_dict[network_name]
                    container_names.append(container_name)
                    container_added = True
                    break
            assert container_added, f"Network {network_name} not found in the queue"

    def _start_chrome_container(self, network_name: str, container_name: str) -> None:
        # 启动Chrome浏览器容器
        self.logger.debug(f"Starting container {container_name}")

        # 配置卷映射
        volumes = {"/dev/shm": {"bind": "/dev/shm", "mode": "rw"}}

        # 健康检查配置
        healthcheck = {
            "test": "curl -f http://localhost:4444",
            "interval": 1 * 10**7,
            "timeout": 1 * 10**7,
            "retries": 100,
            "start_period": 1 * 10**7,
        }

        # 运行Chrome容器
        self.client.containers.run(
            image="selenium/standalone-chrome:3.141.59-dubnium",
            auto_remove=True,
            detach=True,
            tty=True,
            stdin_open=True,
            name=container_name,
            volumes=volumes,
            shm_size="2gb",
            healthcheck=healthcheck,
        )
        # 连接到网络
        self.client.networks.get(network_name).connect(
            container=container_name, aliases=[CHROME_CONTAINER_NAME]
        )

    def _start_runtime_container(self, network_name: str, container_name: str) -> None:
        # 启动运行时环境容器
        self.logger.debug(f"Starting container {container_name}")

        # 配置应用目录映射
        volumes = {os.path.join(os.getcwd(), "apps"): {"bind": "/home", "mode": "rw"}}

        # 运行运行时容器
        self.client.containers.run(
            image="webtestexec:latest",
            auto_remove=True,
            detach=True,
            tty=True,
            stdin_open=True,
            name=container_name,
            volumes=volumes,
            command="bash",
        )
        # 连接到网络
        self.client.networks.get(network_name).connect(
            container=container_name, aliases=[RUNTIME_CONTAINER_NAME]
        )

    @abstractmethod
    def _start_application_container(
        self, network_name: str, container_name: str
    ) -> None:
        # 抽象方法: 启动应用容器 (由具体应用执行器实现)
        raise NotImplementedError("Method not implemented")

    def stop_container_by_name(
        self,
        network_name: str,
        container_name: str,
        remove_container_from_network: bool = False,
    ) -> None:
        # 按名称停止特定容器
        try:
            container = self.client.containers.get(container_name)
            self.logger.debug(f"Stopping container {container_name}")

            container.stop()

            # 等待容器停止
            try:
                max_counter = 100
                while container.status != "exited" and max_counter > 0:
                    time.sleep(0.1)
                    max_counter -= 1
                    container.reload()
            except docker.errors.NotFound:
                pass

            if max_counter == 0:
                raise RuntimeError(f"Container {container_name} did not stop in time")

            # 如果指定, 从网络队列中移除容器
            if remove_container_from_network:
                network_dict_to_remove = None
                for network_dict in self.network_queue:
                    if network_name in network_dict:
                        container_names = network_dict[network_name]
                        container_names.remove(container_name)
                        if len(container_names) == 0:
                            network_dict_to_remove = network_dict
                        break

                if network_dict_to_remove:
                    self.network_queue.remove(network_dict_to_remove)

        except docker.errors.NotFound as err:
            self.logger.error(
                f"stop_container_by_name container {container_name} not found: {err}"
            )

    def stop_containers(self, network_name: str) -> None:
        # 停止所有容器并清理网络
        network_dict_to_remove = None

        for network_dict in self.network_queue:
            if network_name in network_dict:
                container_names = network_dict[network_name]
                self.logger.debug(
                    f"Stopping containers {container_names} attached to network {network_name}"
                )

                # 停止每个容器
                for container_name in container_names:
                    self.stop_container_by_name(
                        network_name=network_name,
                        container_name=container_name,
                        remove_container_from_network=False,
                    )

                # 移除网络
                try:
                    network = self.client.networks.get(network_name)
                    network.remove()
                except docker.errors.NotFound:
                    self.logger.error(f"Network {network_name} not found")
                except docker.errors.APIError:
                    # 强制停止所有连接到网络的容器
                    container_ids = (
                        self.client.networks.get(network_name)
                        .attrs["Containers"]
                        .keys()
                    )
                    for container_id in container_ids:
                        container = self.client.containers.get(container_id)
                        container.stop()

                        # 等待容器停止
                        try:
                            max_counter = 100
                            while container.status != "exited" and max_counter > 0:
                                time.sleep(0.1)
                                max_counter -= 1
                                container.reload()
                        except docker.errors.NotFound:
                            pass

                    network = self.client.networks.get(network_name)
                    network.remove()

                network_dict_to_remove = network_dict

        # 从队列中移除网络
        if network_dict_to_remove:
            self.network_queue.remove(network_dict)

    def execute(
        self,
        individual: Individual,
        network_name: str,
        compile_instr: bool,
    ) -> Optional[ExecutionOutput]:
        # 执行测试用例
        if self.is_app_container_ready(network_name=network_name):
            # 将测试用例写入文件
            write_test_case_to_file(
                app_name=self.app_name,
                statements=individual.statements,
                statement_strings=individual.to_string(),
            )

            # 构建执行命令
            if compile_instr:
                cmd = f"bash -c 'cd ./{self.app_name} && ./run_main.sh --compile-instr true'"
            else:
                cmd = f"bash -c 'cd ./{self.app_name} && ./run_main.sh'"
            
            # 获取运行时容器并执行命令
            runtime_container_name = self.get_container_name(
                network_name=network_name, container_type=RUNTIME_CONTAINER_NAME
            )
            runtime_container = self.client.containers.get(runtime_container_name)
            exec_result = runtime_container.exec_run(cmd=cmd)
            self.logger.debug(f"Execution output: {exec_result.output.decode('utf-8')}")
            
            # 返回执行结果
            return ExecutionOutput(
                exit_code=exec_result.exit_code,
                output=exec_result.output.decode("utf-8"),
            )
        return None

    def get_container_name(self, network_name: str, container_type: str) -> str:
        # 获取特定类型容器的名称
        assert container_type in [
            CHROME_CONTAINER_NAME,
            self.app_name,
            RUNTIME_CONTAINER_NAME,
        ], f"Invalid container type: {container_type}"
        
        # 从网络队列中查找容器
        for network_dict in self.network_queue:
            if network_name in network_dict:
                container_names = network_dict[network_name]
                filtered_names = list(
                    filter(
                        lambda container_name: container_type in container_name,
                        container_names,
                    )
                )
                if len(filtered_names) != 1:
                    raise RuntimeError(f"Invalid container names: {filtered_names}")

                return filtered_names[0]
        raise ValueError(f"Network {network_name} not found in the queue")

    def list_all_containers(self) -> List[str]:
        # 列出所有容器
        return [container.name for container in self.client.containers.list(all=True)]

    def list_all_networks(self) -> List[str]:
        # 列出所有网络
        return [network.name for network in self.client.networks.list()]

    def is_app_container_ready(self, network_name: str) -> bool:
        # 检查应用容器是否就绪
        try:
            container_name = self.get_container_name(
                network_name=network_name, container_type=self.app_name
            )
            container = self.client.containers.get(container_name)
            
            # 等待容器健康状态
            max_counter = 100
            while container.health != "healthy" and max_counter > 0:
                time.sleep(1)
                max_counter -= 1
                container.reload()
            if max_counter == 0:
                raise RuntimeError(f"Container {container_name} did not start in time")

            return True

        except docker.errors.NotFound as err:
            self.logger.error(err)
            raise RuntimeError(
                f"is_app_container_ready container {container_name} not found"
            )
        except ValueError as err:
            raise err

    @staticmethod
    def load_executor(app_name: str) -> "Executor":
        # 静态方法: 加载特定应用的执行器
        assert app_name in APP_NAMES, f"Invalid app name: {app_name}"
        assert os.path.exists(
            os.path.join(os.getcwd(), "executors", f"{app_name}_executor.py")
        ), f"Executor file not found: {app_name}_executor.py"
        
        # 动态导入执行器模块
        executor_module = importlib.import_module(f"executors.{app_name}_executor")
        
        # 查找执行器类
        for name, cls in executor_module.__dict__.items():
            if (
                name.lower() == f"{app_name.capitalize()}Executor".lower()
                and issubclass(cls, Executor)
            ):
                return cls()
        raise ValueError(
            f"Executor class not found in executors.{app_name}_executor.py"
        )
