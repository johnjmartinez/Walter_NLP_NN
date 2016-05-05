#!/bin/bash
set -x

PROJECT_ROOT_DIR=`git rev-parse --show-toplevel`

bugRepositoryPath=$PROJECT_ROOT_DIR/SWTBugRepository.xml

bluirResultsFile=$1

python $PROJECT_ROOT_DIR/bluir_analysis.py \
 -r=$bluirResultsFile \
 -b=$bugRepositoryPath \
