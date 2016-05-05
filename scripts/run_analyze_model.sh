#!/bin/bash
set -x

PROJECT_ROOT_DIR=`git rev-parse --show-toplevel`

configPath=$1
structure=$2
topN=$3

python $PROJECT_ROOT_DIR/autoencoder_model.py \
    analyze \
    -g $configPath \
    -s $structure \
    -n $topN \

