#!/bin/bash
set -x

PROJECT_ROOT_DIR=`git rev-parse --show-toplevel`

configPath=$1
structure=$2
topN=$3
confidenceThreshold=$4

python $PROJECT_ROOT_DIR/autoencoder_model.py \
    analyze \
    -g $configPath \
    -s $structure \
    -n $topN \
    -c $confidenceThreshold


# Example Usage
#./scripts/run_analyze_model.sh model_data/configs/model_config_6.txt class 5 0.75

