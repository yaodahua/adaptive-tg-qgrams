# Web应用测试生成实验 - 中文文档

## 项目概述

这是一个用于Web应用自动化测试生成的研究项目（复现），支持多种测试生成策略，包括随机测试、基于距离的测试、q-gram序列测试和q-gram输入测试。项目使用Docker容器化技术来隔离测试环境，确保实验的可重复性。

## 1. 环境安装

### 1.1 手动安装方式（推荐）（我使用的是这个）

#### 1.1.1 安装依赖

首先需要安装以下工具：
- [conda](https://docs.anaconda.com/miniconda/) - Python环境管理工具
- [poetry](https://python-poetry.org/docs/) - Python包依赖管理工具

安装命令：
```bash
cd web-application-code
# 创建Python 3.8虚拟环境
conda create -n webtestgen python=3.8
conda activate webtestgen

# 安装项目依赖，可用阿里云镜像加速
pip install poetry -i https://pypi.aliyun.com/simple
# pip install poetry -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com 备选
poetry install
```

**注意**：如果在`poetry install`过程中遇到`keyring`问题，可以设置环境变量：
```bash
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
```

#### 1.1.2 构建Docker运行时容器

安装[Docker](https://www.docker.com/get-started/)，然后构建测试执行容器：

```bash
# 构建Docker镜像，win系统下载docker desktop，配合wsl2使用
docker build -t webtestexec:latest .
#可换国内镜像加速
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker-0.unsee.tech",
    "https://docker.m.daocloud.io"
  ]


# 编译Java项目（apps文件夹中的Web应用）
docker run --rm --mount type=bind,source="$(pwd)/apps",target=/home/apps --name runtime webtestexec:latest bash -c 'for app in $(ls /home/apps); do cd /home/apps/$app; mvn clean compile; done'
```

### 1.2 Vagrant自动化安装

**重要提示**：手动安装和Vagrant安装只能选择一种方式，因为两种方式会创建不同的文件权限，可能导致冲突。

如果你希望使用虚拟机环境，可以安装：
- [Vagrant](https://developer.hashicorp.com/vagrant/install) - 虚拟机管理工具
- [Virtualbox](https://www.virtualbox.org/wiki/Downloads) - 虚拟机软件

安装命令：
```bash
vagrant up    # 启动并配置虚拟机
vagrant ssh   # 登录虚拟机
exit          # 退出虚拟机
vagrant halt  # 关闭虚拟机
```



## 2. 运行实验

### 2.1 完整实验运行
```bash
# 运行前先给应用的shell脚本添加可执行权限
chmod +x /home/wlsju/adaptive-tg-qgrams/web-application-code/apps/*/*.sh
#用以下命令验证权限是否仍然存在，一般执行一次即可，如果显示类似 -rwxr-xr-x （有 x 标志），说明权限仍然有效。
ls -l /home/wlsju/adaptive-tg-qgrams/web-application-code/apps/dimeshift/run_main.sh
```
为了验证环境配置是否正确，可以运行快速测试,这个测试只运行2分钟，使用随机策略，适合快速验证环境。：

```bash
conda activate webtestgen
bash -i run_experiments.sh --app-name dimeshift --num-repetitions 1 --budget 60 --strategy random
bash -i run_experiments.sh --app-name dimeshift --num-repetitions 1 --budget 120 --strategy qgrams
```


以下命令会运行所有测试策略（random、distance、qgrams_sequence、qgrams_input），针对dimeshift应用，重复1次，总时间预算为28800秒（8小时）：

```bash
conda activate webtestgen
#运行所有策略
bash -i run_experiments.sh --app-name dimeshift --num-repetitions 1 --budget 28800 --strategy all
#运行随机策略
bash -i run_experiments.sh --app-name dimeshift --num-repetitions 1 --budget 28800 --strategy random
#运行基于距离的策略
bash -i run_experiments.sh --app-name dimeshift --num-repetitions 1 --budget 28800 --strategy distance
#运行q-gram序列策略
bash -i run_experiments.sh --app-name dimeshift --num-repetitions 1 --budget 28800 --strategy qgrams --diversity-strategy sequence
#运行q-gram输入策略
bash -i run_experiments.sh --app-name dimeshift --num-repetitions 1 --budget 28800 --strategy qgrams --diversity-strategy input
```

### 2.2 系统架构说明

运行实验时会启动三个Docker容器：
1. **runtime容器** - 执行测试用例
2. **chrome容器** - 提供浏览器环境
3. **应用容器**（如dimeshift） - 运行被测试的Web应用

这些容器通过Docker网络连接，第一次运行时会自动下载chrome和应用容器。

### 2.3 支持的Web应用

项目支持以下Web应用：
- `dimeshift` - 时间管理应用
- `pagekit` - CMS系统
- `petclinic` - 宠物诊所管理系统
- `phoenix` - 现代化Web框架示例
- `retroboard` - 敏捷开发看板工具
- `splittypie` - 费用分摊应用

### 2.4 快速测试

为了验证环境配置是否正确，可以运行快速测试：

```bash
conda activate webtestgen
bash -i run_experiments.sh --app-name dimeshift --num-repetitions 1 --budget 60 --strategy random
bash -i run_experiments.sh --app-name dimeshift --num-repetitions 1 --budget 120 --strategy qgrams
```

这个测试只运行2分钟，使用随机策略，适合快速验证环境。

### 2.5 清理命令

实验完成后，清理Docker容器和网络：

```bash
# 停止所有容器
docker stop $(docker ps -aq)

# 清理无用资源
docker system prune -f
```
### 2.6 docker常用命令

- `docker ps -a` - 查看所有容器（包括已停止的）
- `docker stop <container_id>` - 停止指定容器
- `docker rm <container_id>` - 删除指定容器
- `docker network prune -f` - 清理无用网络
- `docker rm -f $(docker ps -aq)` - ⚠️ 危险命令，强制删除所有容器

## 3. 项目特点

### 3.1 测试生成策略
- **random** - 随机测试生成
- **distance** - 基于距离的测试生成
- **qgrams_sequence** - 基于q-gram序列的测试生成
- **qgrams_input** - 基于q-gram输入的测试生成

### 3.2 技术栈
- **Python 3.8** - 主要编程语言
- **Docker** - 容器化技术
- **Selenium** - Web自动化测试
- **Maven** - Java项目构建
- **Spring Boot** - Web应用框架

### 3.3 实验特性
- 完全容器化的测试环境
- 多种测试生成策略比较
- 可重复的实验设置
- 详细的测试覆盖率报告

## 4. 故障排除

### 4.1 常见问题

1. **网络连接问题**：在中国大陆可能需要配置Docker镜像源或使用代理
2. **权限问题**：确保Docker服务正常运行，当前用户有足够权限
3. **依赖下载失败**：检查网络连接，必要时配置国内镜像源

### 4.2 获取帮助

如果遇到问题，可以：
1. 检查Docker服务状态：`sudo systemctl status docker`
2. 验证网络连接：`ping docker.io`
3. 查看详细错误日志

## 5. 项目结构

- `apps/` - 包含所有Web应用的Java源代码
- `executors/` - 测试执行器
- `generators/` - 测试用例生成器
- `selenium-custom-library/` - 自定义Selenium库
- `scripts/` - 运行脚本

这个项目为Web应用自动化测试研究提供了完整的实验平台，支持多种先进的测试生成技术。