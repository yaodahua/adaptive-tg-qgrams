from config import CHROME_CONTAINER_NAME, DIMESHIFT_NAME
from executors.executor import Executor
import time

from global_log import GlobalLog

# DimeshiftExecutor 执行器 用于执行 Dimeshift 应用
class DimeshiftExecutor(Executor):

    def __init__(self):
        super().__init__(app_name=DIMESHIFT_NAME)
        self.logger = GlobalLog("DimeshiftExecutor")

    # 启动 Dimeshift 应用容器
    def _start_application_container(
        self, network_name: str, container_name: str
    ) -> None:

        self.logger.debug(f"Starting container {container_name}")

        # 定义容器健康检查
        healthcheck = {
            "test": "curl -f http://localhost:8080",
            "interval": 1 * 10**9,
            "timeout": 5 * 10**9,
            "retries": 20,
            "start_period": 5 * 10**9,
        }

        self.client.containers.run(
            image="dockercontainervm/dimeshift:latest",
            auto_remove=True,
            detach=True,
            tty=True,
            stdin_open=True,
            name=container_name,
            entrypoint="./run-services-docker.sh",
            working_dir="/home/dimeshift-application",
            healthcheck=healthcheck,
            command="bash",
        )

        self.client.networks.get(network_name).connect(
            container=container_name, aliases=[self.app_name]
        )

#
if __name__ == "__main__":
    executor = DimeshiftExecutor()
    network_name = executor.start_containers()
    chrome_container_name = None
    # 启动 Chrome 容器
    for i in range(5):

        try:
            _ = executor.get_container_name(
                network_name=network_name, container_type=CHROME_CONTAINER_NAME
            )
        except RuntimeError:
            assert chrome_container_name is not None, "Chrome container name is None"
            executor.start_container_by_name(
                network_name=network_name,
                container_name=chrome_container_name,
                add_container_to_network=True,
            )

        print("Executing test...")
        time.sleep(3)

        chrome_container_name = executor.get_container_name(
            network_name=network_name, container_type=CHROME_CONTAINER_NAME
        )
        executor.stop_container_by_name(
            network_name=network_name,
            container_name=chrome_container_name,
            remove_container_from_network=True,
        )

    executor.stop_containers(network_name=network_name)
