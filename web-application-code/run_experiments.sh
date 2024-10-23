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

conda activate webtestgen
conda env list

app_name="dimeshift"
num_repetitions=10
budget=300
strategy="all"
diversity_strategy="sequence"
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
    done
elif [[ $strategy == "all_but_random" ]]; then
    for i in $(seq 1 $num_repetitions); do
        run_distance $app_name $i $budget sequence 
        run_qgrams $app_name $i $budget sequence 
        run_qgrams $app_name $i $budget input 
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
else
    echo "Invalid strategy: " $strategy
    exit 1
fi



