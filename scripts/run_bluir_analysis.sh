#!/bin/bash
set -x

PROJECT_ROOT_DIR=`git rev-parse --show-toplevel`

bugRepositoryPath=$PROJECT_ROOT_DIR/SWTBugRepository.xml

bluirResultsFile=$1

python $PROJECT_ROOT_DIR/bluir_analysis.py \
 -r=$bluirResultsFile \
 -b=$bugRepositoryPath \

# Example Usage
# for file in `ls results`; do ./scripts/run_bluir_analysis.sh results/$file | tee analysis/${file/results/analysis}; done