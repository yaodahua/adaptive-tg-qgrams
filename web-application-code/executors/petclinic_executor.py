from config import PETCLINIC_NAME
from executors.executor import Executor

from global_log import GlobalLog


class PetclinicExecutor(Executor):

    def __init__(self):
        super().__init__(app_name=PETCLINIC_NAME)
        self.logger = GlobalLog("PetclinicExecutor")

    def _start_application_container(
        self, network_name: str, container_name: str
    ) -> None:

        self.logger.debug(f"Starting container {container_name}")

        healthcheck = {
            "test": "curl -f http://localhost:8080",
            "interval": 5 * 10**9,
            "timeout": 5 * 10**9,
            "retries": 100,
            "start_period": 5 * 10**9,
        }

        self.client.containers.run(
            image="dockercontainervm/petclinic:latest",
            auto_remove=True,
            detach=True,
            tty=True,
            stdin_open=True,
            name=container_name,
            entrypoint="./run-services-docker.sh",
            environment=[
                "PATH=/root/workspace/maven/apache-maven-3.5.4/bin:/root/workspace/java/jdk1.8.0_181/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
            ],
            working_dir="/home/spring-petclinic-angularjs",
            healthcheck=healthcheck,
            command="bash",
        )

        self.client.networks.get(network_name).connect(
            container=container_name, aliases=[self.app_name]
        )
