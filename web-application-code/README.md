# Code to Replicate Web Application Experiments

## 1. Installation

### 1.1 Manual setup

#### 1.1.1 Install dependencies

Install [conda](https://docs.anaconda.com/miniconda/) for your system, as well as [poetry](https://python-poetry.org/docs/). Then type:

```commandline
conda create -n webtestgen python=3.8
conda activate webtestgen
poetry install
```

If it gets stuck in `keyring` when `poetry install`, try to use `export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring`.

#### 1.1.2 Build runtime docker container

Install [docker](https://www.docker.com/get-started/) for your system. For Linux, install the [community edition](https://docs.docker.com/engine/install/).

```commandline
docker build -t webtestexec:latest .
```

and compile the Java projects inside the `apps` folder with

```commandline
docker run --rm --mount type=bind,source="$(pwd)/apps",target=/home/apps --name runtime webtestexec:latest bash -c 'for app in $(ls /home/apps); do cd /home/apps/$app; mvn clean compile; done'
```

### 1.2 Vagrant setup 

Install [vagrant](https://developer.hashicorp.com/vagrant/install) and an hypervisor, e.g., [Virtualbox](https://www.virtualbox.org/wiki/Downloads). Then, from the root of the repository type:

```commandline
vagrant up # this sets up the virtual machine with all the required dependencies
vagrant ssh # to access the machine
exit # to exit the machine 
vagrant halt # to stop the machine
```

All the commands below should be prefixed by `vagrant ssh` if using this setup. Use either of the two setups, as the `vagrant up` command will fail if Java applications have been compiled with the manual setup (`docker` writes the `target` directory when using `mvn` using the admin user and `vagrant` tries to delete those directories).

## 2. Running the experiments

The following command runs `all` the techniques, namely `random`, `distance`, `qgrams_sequence` and `qgrams_input` for `1` repetition and `28800` seconds (i.e., 8 hours), considering the `dimeshift` subject.

```commandline
conda activate webtestgen
bash -i run_experiments.sh --app-name dimeshift --num-repetitions 1 --budget 28800 --strategy all
```

The command starts three docker containers connected through a docker network. The `runtime` container, built at step 1.1.2, that executes the tests, the `chrome` container explosing the browser, and the `dimeshift` container, including the web application. The `chrome` container and the `dimeshift` container, will be downloaded the first time the command is executed. 

The other web application subjects are: `pagekit`, `petclinic`, `phoenix`, `retroboard` and `splittypie`.

A quick smoke test to see if everything is setup correctly is:

```commandline
conda activate webtestgen
bash -i run_experiments.sh --app-name dimeshift --num-repetitions 1 --budget 120 --strategy random
```

If you need to stop all containers and delete the dangling networks type:

```commandline
docker stop $(docker ps -aq)
docker system prune -f
```

