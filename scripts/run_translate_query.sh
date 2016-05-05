#!/bin/bash
set -x

PROJECT_ROOT_DIR=`git rev-parse --show-toplevel`

indriQueryPath=$PROJECT_ROOT_DIR/testRunOut/query

configPath=$1
translatedQueryPath=$2

python $PROJECT_ROOT_DIR/translate_query.py \
    -g $configPath \
    -i $indriQueryPath \
    -t $translatedQueryPath \
    -c 0.75 0.85 0.95 \

# Example
# for i in `seq 1 6`; do ./run_translate_query.sh model_data/configs/model_config_$i.txt translated_queries/translated_query_$i.xml; done