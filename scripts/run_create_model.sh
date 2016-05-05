#!/bin/bash
set -x

PROJECT_ROOT_DIR=`git rev-parse --show-toplevel`

configPath=$1

python $PROJECT_ROOT_DIR/autoencoder_model.py \
    create \
    -g $configPath \

# Example Usage
# for i in `seq 1 12; do ./run_create_model.sh model_data/configs/model_config_$i.txt; done