#!/bin/bash
set -x

PROJECT_ROOT_DIR=`git rev-parse --show-toplevel`

configPath=$1

python $PROJECT_ROOT_DIR/autoencoder_model.py \
    create \
    -g $configPath \

# Example
# for i in `seq 1 6`; do ./run_create_corpuses.sh corpus_data/configs/corpus_config_$i.txt; done