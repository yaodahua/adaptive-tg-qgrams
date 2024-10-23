from config import RETROBOARD_NAME
from executors.executor import Executor

from global_log import GlobalLog


class RetroboardExecutor(Executor):

    def __init__(self):
        super().__init__(app_name=RETROBOARD_NAME)
        self.logger = GlobalLog("PhoenixExecutor")

    def _start_application_container(
        self, network_name: str, container_name: str
    ) -> None:

        self.logger.debug(f"Starting container {container_name}")

        healthcheck = {
            "test": "curl -f http://localhost:8080",
            "interval": 1 * 10**9,
            "timeout": 5 * 10**9,
            "retries": 20,
            "start_period": 5 * 10**9,
        }

        self.client.containers.run(
            image="dockercontainervm/retroboard:latest",
            auto_remove=True,
            detach=True,
            tty=True,
            stdin_open=True,
            name=container_name,
            entrypoint="./run-services-docker.sh",
            working_dir="/home/retro-board",
            healthcheck=healthcheck,
            command="bash",
        )

        self.client.networks.get(network_name).connect(
            container=container_name, aliases=[self.app_name]
        )
