# Web 应用测试项目说明

## 项目概述

这是一个基于自适应随机测试 art 和 Q-gram、simidf、tfidf、dist、random 的 Web 应用自动化测试框架。项目采用容器化docker技术,支持多种测试用例生成策略,用于评估 Web 应用的测试覆盖率和性能。

## 项目结构详解

### 核心模块

#### 1. 应用模块 (apps/)

- **功能**: 包含 6 个 Java Web 应用测试目标
- **应用列表**: dimeshift, pagekit, petclinic, phoenix, retroboard, splittypie
- **特点**: 每个应用都有完整的 Maven 配置和 Docker 容器化部署

#### 2. 执行器模块 (executors/)

- **功能**: 管理 Docker 容器和测试执行
- **核心文件**:
  - `executor.py` - 抽象基类,管理容器生命周期
  - `execution_output.py` - 执行结果解析
  - 各应用专属执行器 (如 dimeshift_executor.py)

#### 3. 生成器模块 (generators/)

- **功能**: 实现多种测试用例生成算法
- **生成策略**:
  - `random_test_case_generator.py` - 随机生成
  - `distance_test_case_generator.py` - 基于距离的生成
  - `qgrams_test_case_generator.py` - 基于 Q-gram 的生成
  - `length_test_case_generator.py` - 基于长度的生成
  - `simidf_test_case_generator.py` - 基于相似度 IDF 的生成
  - `tfidf_test_case_generator.py` - 基于 TF-IDF 的生成

#### 4. 个体管理模块 (individuals/)

- **功能**: 管理测试用例个体和多样性计算
- **核心文件**:
  - `individual.py` - 个体类,实现距离度量和 Q-gram 分析
  - `id_generator.py` - 唯一 ID 生成器

#### 5. 语句定义模块 (statements/)

- **功能**: 定义测试用例中的各种语句类型
- **语句类型**:
  - 类声明语句
  - 方法调用语句
  - 变量声明语句
  - 枚举语句
  - 重置语句

#### 6. 代码解析模块 (parsing/)

- **功能**: 解析 Java 代码结构和生成代码图
- **核心功能**:
  - 类解析
  - 图解析
  - 代码插桩
  - 反解析工具

### 工具和配置模块

#### 1. 配置管理

- `config.py` - 项目常量配置
- `config_variables.py` - 配置变量定义

#### 2. 日志和工具

- `global_log.py` - 全局日志管理
- `utils/` - 工具函数集合
  - `file_utils.py` - 文件操作工具
  - `randomness_utils.py` - 随机数工具
  - `stats_utils.py` - 统计工具

#### 3. 主程序入口

- `main.py` - 主程序,控制测试流程
- `execute_test_suite.py` - 测试套件执行

### 分析和可视化模块

#### 1. 分析脚本

- `analyze.py` - 综合性能分析
- `analyze_coverage.py` - 覆盖率深度分析

#### 2. 图表生成

- `graphs/` - 存储代码图结构
- 生成 SVG 格式的覆盖率变化图和测试长度变化图

### 运行脚本

- `run_experiments.sh` - 实验运行脚本
- `run_analysis.sh` - 分析运行脚本
- `download_all_apps.sh` - 应用下载脚本

## 技术特点

### 1. 容器化技术

- 使用 Docker 容器隔离测试环境
- 包含 Chrome 浏览器容器、运行时容器和应用容器
- 支持网络管理和容器健康检查

### 2. 多样性策略

- 支持序列多样性和输入多样性两种策略
- 使用编辑距离和 Q-gram 技术计算测试用例差异
- 基于信息熵选择最优测试用例

### 3. 自适应测试

- 结合进化算法和多样性度量
- 动态调整测试用例生成策略
- 支持多种测试目标优化

### 4. 统计分析

- 计算覆盖率指标和 AUC 值
- 执行统计显著性检验
- 生成 Excel 格式的分析报告

## 工作流程

### 1. 环境准备

- 下载目标 Web 应用
- 构建 Docker 容器环境
- 配置测试参数

### 2. 测试生成

- 选择测试用例生成策略
- 生成测试用例个体
- 评估测试用例多样性

### 3. 测试执行

- 启动容器环境
- 执行测试用例
- 收集执行结果

### 4. 结果分析

- 计算覆盖率指标
- 生成可视化图表
- 执行统计检验

## 输出文件

### 1. 日志文件

- 执行日志和错误日志
- 覆盖率统计日志

### 2. 数据文件

- Excel 格式的指标表格
- 包含 RQs 和 Others 工作表

### 3. 图表文件

- SVG 格式的可视化图表
- 覆盖率变化趋势图
- 测试长度变化图

## 依赖环境

### 1. 系统要求

- Linux 操作系统
- Docker 环境
- Python 3.8+

### 2. Python 依赖

- 使用 Poetry 管理依赖
- 主要依赖: docker, selenium, numpy, scipy, matplotlib

### 3. 容器镜像

- selenium/standalone-chrome - Chrome 浏览器
- webtestexec:latest - 自定义运行时环境
- 各应用专属镜像

## 使用说明

### 1. 快速开始

```bash
# 下载所有应用
./download_all_apps.sh

# 运行实验
./run_experiments.sh

# 分析结果
./run_analysis.sh
```

### 2. 自定义配置

- 修改 config.py 中的参数
- 选择不同的测试生成策略
- 调整时间预算和迭代次数

### 3. 结果解读

- 查看 analyze.log 了解覆盖率统计
- 分析 table_metrics.xlsx 中的指标
- 查看 SVG 图表了解趋势变化

## 项目价值

这个项目为 Web 应用自动化测试提供了:

- 可复现的实验环境
- 多种测试生成策略比较
- 详细的性能评估指标
- 科学的统计分析方法

适用于软件测试研究、测试工具开发和教学质量评估等多个场景。
