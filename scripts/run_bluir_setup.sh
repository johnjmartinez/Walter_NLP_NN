#!/bin/bash
set -x

PROJECT_ROOT_DIR=`git rev-parse --show-toplevel`

source ${PROJECT_ROOT_DIR}/scripts/bluir_paths.sh

mkdir -p ${bluirOutDir}

cd ${bluirHome}

#create query from XML Bug Repository
$jBLUiR -task='createquery' \
 -bugRepoLocation=${bluirBugRepo} \
 -queryFilePath=${bluirOutDir}/query

#construct a structured document collection from source code files
$jBLUiR -task='createdocs' \
 -codeLocation=${bluirSrcRepo} \
 -docLocation=${bluirOutDir}/docs

#index document collection
$jBLUiR -task='index' \
 -indexLocation=${bluirOutDir}/index \
 -docLocation=${bluirOutDir}/docs

# Example Usage
# ./scripts/run_bluir_setup.sh