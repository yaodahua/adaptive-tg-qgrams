#!/bin/bash

conda activate webtestgen
conda env list

results_folder_name="none"
percentage_iterations=50

while [ $# -gt 0 ] ; do
  case $1 in
    -r | --results-folder-name) results_folder_name="$2" ;;
    -p | --percentage-iterations) percentage_iterations="$2" ;;
  esac
  shift
done

if [[ $results_folder_name == "none" ]]; then
    echo "Invalid results folder name: " $results_folder_name
    exit 1
fi

for app_name in "dimeshift" "pagekit" "petclinic" "phoenix" "retroboard" "splittypie"; do
    python analyze.py --app-name $app_name --results-folder-name $results_folder_name --percentage-iterations $percentage_iterations
    python analyze_coverage.py --app-name $app_name --results-folder-name $results_folder_name
done




