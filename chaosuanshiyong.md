好的！为你总结在超算上使用Slurm跑任务的完整流程：

## 🚀 Slurm使用完整流程

### 1. 准备工作
```bash
# 登录超算
ssh username@10.10.246.177

# 准备环境（在.bashrc中已配置好）
conda activate your_env
```

### 2. 选择合适的分区
根据你的任务类型选择：

| 任务类型 | 推荐分区 | 资源申请 |
|---------|----------|----------|
| **CPU任务** | `x86_64` 或 `x86_64_l` | `--cpus-per-task=数字` |
| **GPU任务** | `x86_64_GPU` | `--gres=gpu:A800:数字` |
| **大内存任务** | `x86_64_l` | 自动获得2TB内存 |
| **不指定** | `x86_64_all` | 系统自动选择 |

### 3. 创建Slurm提交脚本
创建 `submit_job.sh`：
```bash
#!/bin/bash
#SBATCH --job-name=my_job          # 作业名称
#SBATCH --partition=x86_64_GPU     # 选择分区
#SBATCH --nodes=1                  # 节点数
#SBATCH --ntasks-per-node=1        # 每个节点任务数
#SBATCH --cpus-per-task=4          # 每个任务CPU核心数
#SBATCH --gres=gpu:A800:1          # GPU数量（如需要）
#SBATCH --output=job_%j.log        # 输出日志
#SBATCH --error=job_%j.err         # 错误日志

# 环境设置
module load anaconda
conda activate your_env

# 运行你的任务
python your_script.py
```

### 4. 常用资源申请模板

#### CPU任务模板：
```bash
#!/bin/bash
#SBATCH --job-name=cpu_task
#SBATCH --partition=x86_64
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32         # 申请32核心
#SBATCH --output=%j.log

python cpu_intensive_script.py
```

#### GPU任务模板：
```bash
#!/bin/bash
#SBATCH --job-name=gpu_task
#SBATCH --partition=x86_64_GPU
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8          # 建议GPU:CPU=1:4或1:8
#SBATCH --gres=gpu:A800:2          # 申请2张A800
#SBATCH --output=%j.log

python gpu_script.py
```

### 5. 提交和管理作业

```bash
# 提交作业
sbatch submit_job.sh

# 查看作业队列
squeue
squeue -u $USER                    # 只看自己的作业

# 查看作业详情
scontrol show job <job_id>

# 终止作业
scancel <job_id>
scancel -u $USER                   # 终止所有自己的作业

# 查看作业历史
sacct
```

### 6. 监控资源状态

```bash
# 查看节点状态
sinfo
sinfo -p x86_64_GPU -o "%N %P %G %T %C"  # 查看GPU分区

# 查看详细资源
scontrol show node gpu-n1
```

### 7. 实用技巧

#### 实时监控作业：
```bash
# 每30秒刷新队列
watch -n 30 'squeue -u $USER'

# 实时查看作业输出
tail -f job_12345.log
```

#### 依赖作业（一个接一个运行）：
```bash
# 第二个作业依赖第一个作业完成
sbatch --dependency=afterok:12345 job2.sh
```

#### 邮件通知：
```bash
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=your_email@example.com
```

## 📋 快速开始示例

### 步骤1：创建测试脚本
```python
# test_slurm.py
import time
print("Slurm任务开始运行!")
time.sleep(10)
print("任务完成!")
```

### 步骤2：创建提交脚本
```bash
# test_job.sh
#!/bin/bash
#SBATCH --job-name=test
#SBATCH --partition=x86_64
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --output=test_%j.log

python test_slurm.py
```

### 步骤3：提交并监控
```bash
chmod +x test_job.sh
sbatch test_job.sh
squeue -u $USER
tail -f test_12345.log
```

## ⚠️ 重要提醒

1. **不要**在管理节点直接运行计算任务
2. **所有计算**必须通过Slurm提交
3. **合理申请资源**，不要过度申请
4. **及时查看日志**了解任务状态
5. **任务完成后**清理临时文件

## 🆘 遇到问题怎么办

```bash
# 查看作业为什么在排队
squeue -o "%.18i %.9P %.8j %.8u %.2t %.10M %.6D %.4C %.12b %N"

# 查看详细的错误信息
cat job_12345.err

# 联系管理员
# 夏丛紫: ccongzi@163.com
```

按照这个流程，你就能顺利在超算上运行任务了！先从简单的测试开始，熟悉后再运行你的正式任务。