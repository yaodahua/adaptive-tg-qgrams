#!/bin/bash

run_random() {

    local app_name_local=$1
    local num_repetitions_local=$2
    local budget_local=$3
    local resume_filepath_local=$4
    
    mkdir -p results/$app_name_local/random

    if [ -z "$resume_filepath_local" ]; then
        resume_filepath_local="none"
    fi

    if [[ $resume_filepath_local != "none" ]]; then
        echo "[$app_name_local] Resuming random experiment $i"
        python main.py --app-name $app_name_local --generator-name random --budget $budget_local \
            --progress --max-length 40 --resume-filepath $resume_filepath_local > results/$app_name_local/random/random_${i}.log
        return
    fi

    echo "[$app_name_local] Running random experiment $i"
    python main.py --app-name $app_name_local --generator-name random --budget $budget_local \
        --progress --max-length 40 > results/$app_name_local/random/random_${i}.log
    
}

run_distance() {

    local app_name_local=$1
    local num_repetitions_local=$2
    local budget_local=$3
    local diversity_strategy_local=$4
    local resume_filepath_local=$5
    
    mkdir -p results/$app_name_local/distance_$diversity_strategy_local

    if [ -z "$resume_filepath_local" ]; then
        resume_filepath_local="none"
    fi

    if [[ $resume_filepath_local != "none" ]]; then
        echo "[$app_name_local] Resuming distance $diversity_strategy_local experiment $i"
        python main.py --app-name $app_name_local --generator-name distance --budget $budget_local \
            --progress --max-length 40 --num-candidates 30 --diversity-strategy $diversity_strategy_local \
            --resume-filepath $resume_filepath_local \
            > results/$app_name_local/distance_$diversity_strategy_local/distance_$diversity_strategy_local_${i}.log
        return
    fi

    echo "[$app_name_local] Running distance $diversity_strategy_local experiment $i"
    python main.py --app-name $app_name_local --generator-name distance --budget $budget_local \
        --progress --max-length 40 --num-candidates 30 --diversity-strategy $diversity_strategy_local \
        > results/$app_name_local/distance_$diversity_strategy_local/distance_$diversity_strategy_local_${i}.log

}

run_qgrams() {

    local app_name_local=$1
    local num_repetitions_local=$2
    local budget_local=$3
    local diversity_strategy_local=$4
    local resume_filepath_local=$5
    
    mkdir -p results/$app_name_local/qgrams_$diversity_strategy_local

    if [ -z "$resume_filepath_local" ]; then
        resume_filepath_local="none"
    fi

    if [[ $resume_filepath_local != "none" ]]; then
        echo "[$app_name_local] Resuming qgrams $diversity_strategy_local experiment $i"
        python main.py --app-name $app_name_local --generator-name qgrams --budget $budget_local \
            --progress --max-length 40 --num-candidates 30 --diversity-strategy $diversity_strategy_local \
            --resume-filepath $resume_filepath_local \
            > results/$app_name_local/qgrams_$diversity_strategy_local/qgrams_$diversity_strategy_local_${i}.log
        return
    fi

    echo "[$app_name_local] Running qgrams $diversity_strategy_local experiment $i"
    python main.py --app-name $app_name_local --generator-name qgrams --budget $budget_local \
        --progress --max-length 40 --num-candidates 30 --diversity-strategy $diversity_strategy_local \
        > results/$app_name_local/qgrams_$diversity_strategy_local/qgrams_$diversity_strategy_local_${i}.log

}

run_simidf() {

    local app_name_local=$1
    local num_repetitions_local=$2
    local budget_local=$3
    local diversity_strategy_local=$4
    local resume_filepath_local=$5
    
    mkdir -p results/$app_name_local/simidf_$diversity_strategy_local

    if [ -z "$resume_filepath_local" ]; then
        resume_filepath_local="none"
    fi

    if [[ $resume_filepath_local != "none" ]]; then
        echo "[$app_name_local] Resuming simidf $diversity_strategy_local experiment $i"
        python main.py --app-name $app_name_local --generator-name simidf --budget $budget_local \
            --progress --max-length 40 --num-candidates 30 --diversity-strategy $diversity_strategy_local \
            --resume-filepath $resume_filepath_local \
            > results/$app_name_local/simidf_$diversity_strategy_local/simidf_$diversity_strategy_local_${i}.log
        return
    fi

    echo "[$app_name_local] Running simidf $diversity_strategy_local experiment $i"
    python main.py --app-name $app_name_local --generator-name simidf --budget $budget_local \
        --progress --max-length 40 --num-candidates 30 --diversity-strategy $diversity_strategy_local \
        > results/$app_name_local/simidf_$diversity_strategy_local/simidf_$diversity_strategy_local_${i}.log

}

run_tfidf() {

    local app_name_local=$1
    local num_repetitions_local=$2
    local budget_local=$3
    local diversity_strategy_local=$4
    local resume_filepath_local=$5
    
    mkdir -p results/$app_name_local/tfidf_$diversity_strategy_local

    if [ -z "$resume_filepath_local" ]; then
        resume_filepath_local="none"
    fi

    if [[ $resume_filepath_local != "none" ]]; then
        echo "[$app_name_local] Resuming tfidf $diversity_strategy_local experiment $i"
        python main.py --app-name $app_name_local --generator-name tfidf --budget $budget_local \
            --progress --max-length 40 --num-candidates 30 --diversity-strategy $diversity_strategy_local \
            --resume-filepath $resume_filepath_local \
            > results/$app_name_local/tfidf_$diversity_strategy_local/tfidf_$diversity_strategy_local_${i}.log
        return
    fi

    echo "[$app_name_local] Running tfidf $diversity_strategy_local experiment $i"
    python main.py --app-name $app_name_local --generator-name tfidf --budget $budget_local \
        --progress --max-length 40 --num-candidates 30 --diversity-strategy $diversity_strategy_local \
        > results/$app_name_local/tfidf_$diversity_strategy_local/tfidf_$diversity_strategy_local_${i}.log

}

conda activate webtestgen
conda env list

# 实验参数默认值
app_name="dimeshift"
num_repetitions=10 #每个策略重复运行的次数
budget=300 # 运行时间，单位是秒，论文中是8小时，即28800秒
strategy="all"
diversity_strategy="sequence" #有两种策略：sequence和input，针对q-gram序列和输入分别进行测试用例生成
resume_filepath="none"

while [ $# -gt 0 ] ; do
  case $1 in
    -a | --app-name) app_name="$2" ;;
    -n | --num-repetitions) num_repetitions="$2" ;;
    -b | --budget) budget="$2" ;;
    -s | --strategy) strategy="$2" ;;
    -d | --diversity-strategy) diversity_strategy="$2" ;;
    -r | --resume-filepath) resume_filepath="$2" ;;
  esac
  shift
done

if [[ $app_name != "dimeshift" && $app_name != "pagekit" && $app_name != "petclinic" \
        && $app_name != "phoenix" && $app_name != "retroboard" && $app_name != "splittypie" ]]; then
    echo "Invalid app name: " $app_name
    exit 1
fi

if [[ $num_repetitions -lt 1 ]]; then
    echo "Invalid number of repetitions: " $num_repetitions
    exit 1
fi

if [[ $budget -lt 1 ]]; then
    echo "Invalid budget: " $budget
    exit 1
fi

if [[ $strategy == "all" ]]; then
    for i in $(seq 1 $num_repetitions); do
        run_random $app_name $i $budget 
        run_distance $app_name $i $budget sequence 
        run_qgrams $app_name $i $budget sequence 
        run_qgrams $app_name $i $budget input 
        run_simidf $app_name $i $budget sequence 
        run_simidf $app_name $i $budget input 
        run_tfidf $app_name $i $budget sequence 
        run_tfidf $app_name $i $budget input 
    done
elif [[ $strategy == "all_but_random" ]]; then
    for i in $(seq 1 $num_repetitions); do
        run_distance $app_name $i $budget sequence 
        run_qgrams $app_name $i $budget sequence 
        run_qgrams $app_name $i $budget input 
        run_simidf $app_name $i $budget sequence 
        run_simidf $app_name $i $budget input 
        run_tfidf $app_name $i $budget sequence 
        run_tfidf $app_name $i $budget input 
    done
elif [[ $strategy == "random" ]]; then
    for i in $(seq 1 $num_repetitions); do
        run_random $app_name $i $budget $resume_filepath
    done
elif [[ $strategy == "distance" ]]; then
    for i in $(seq 1 $num_repetitions); do
        run_distance $app_name $i $budget $diversity_strategy $resume_filepath
    done
elif [[ $strategy == "qgrams" ]]; then
    for i in $(seq 1 $num_repetitions); do
        run_qgrams $app_name $i $budget $diversity_strategy $resume_filepath
    done
elif [[ $strategy == "simidf" ]]; then
    for i in $(seq 1 $num_repetitions); do
        run_simidf $app_name $i $budget $diversity_strategy $resume_filepath
    done
elif [[ $strategy == "tfidf" ]]; then
    for i in $(seq 1 $num_repetitions); do
        run_tfidf $app_name $i $budget $diversity_strategy $resume_filepath
    done
elif [[ $strategy == "new_methods" ]]; then
    for i in $(seq 1 $num_repetitions); do
        run_simidf $app_name $i $budget sequence 
        run_simidf $app_name $i $budget input 
        run_tfidf $app_name $i $budget sequence 
        run_tfidf $app_name $i $budget input 
    done
else
    echo "Invalid strategy: " $strategy
    exit 1
fi



