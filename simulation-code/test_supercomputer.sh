#!/bin/bash
#SBATCH --job-name=test_supercomputer
#SBATCH --partition=x86_64
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --output=test_supercomputer_%j.log

echo "=== 超算平台测试开始 ==="
echo "作业ID: $SLURM_JOB_ID"
echo "测试参数: 字符串长度100, rand方法100次"
echo "开始时间: $(date)"

# 激活conda环境
source /share/anaconda3/etc/profile.d/conda.sh
conda activate simulation

# 运行测试
python test_gen_palindrome.py --max-string-length 100 --runs-rand 100 --runs-dist 0 --runs-bigrams 0 --runs-tfidf 0 --runs-simidf 0

echo "测试完成时间: $(date)"
echo "=== 超算平台测试完成 ==="

