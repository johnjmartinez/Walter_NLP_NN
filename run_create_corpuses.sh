#!/bin/bash
set -x

PROJECT_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

bugRepositoryPath=$PROJECT_ROOT_DIR/SWTBugRepository.xml
indriQueryPath=$PROJECT_ROOT_DIR/testRunOut/query
indriDocumentsFolderPath=$PROJECT_ROOT_DIR/testRunOut/docs

configPath=$1

python $PROJECT_ROOT_DIR/create_corpuses.py \
    -b $bugRepositoryPath \
    -q $indriQueryPath \
    -d $indriDocumentsFolderPath \
    -g $configPath \