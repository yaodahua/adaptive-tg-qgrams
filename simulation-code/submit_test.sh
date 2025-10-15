#!/bin/bash
#SBATCH --job-name=numpy_test
#SBATCH --partition=x86_64
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --output=numpy_test_%j.log

echo "=== NumPy/SciPy测试开始 ==="
echo "作业ID: $SLURM_JOB_ID"

# 方法1：使用conda绝对路径
source /share/anaconda3/etc/profile.d/conda.sh
conda activate simulation

# 运行测试
python test_numpy_scipy.py

echo "=== 测试完成 ==="