#!/bin/bash
#SBATCH --job-name=tfidf_10000_1000
#SBATCH --partition=x86_64
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --output=tfidf_10000_1000_%j.log

echo "=== TF-IDF测试开始 ==="
echo "作业ID: $SLURM_JOB_ID"
echo "字符串长度: 10000"
echo "运行次数: 1000"

# 激活conda环境
source /share/anaconda3/etc/profile.d/conda.sh
conda activate simulation

# 运行TF-IDF测试
python test_gen_palindrome.py --max-string-length 10000 --runs-tfidf 1000 --runs-rand 0 --runs-dist 0 --runs-simidf 0 --runs-bigrams 0

echo "=== TF-IDF测试完成 ==="