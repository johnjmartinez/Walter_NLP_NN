#!/bin/bash
set -x

PROJECT_ROOT_DIR=`git rev-parse --show-toplevel`

bugRepositoryPath=$PROJECT_ROOT_DIR/SWTBugRepository.xml
indriQueryPath=$PROJECT_ROOT_DIR/testRunOut/query
indriDocumentsFolderPath=$PROJECT_ROOT_DIR/testRunOut/docs

configPath=$1

python $PROJECT_ROOT_DIR/create_corpuses.py \
    -b $bugRepositoryPath \
    -q $indriQueryPath \
    -d $indriDocumentsFolderPath \
    -g $configPath \

# Example
# for i in `seq 1 6`; do ./run_create_corpuses.sh corpus_data/configs/corpus_config_$i.txt; done