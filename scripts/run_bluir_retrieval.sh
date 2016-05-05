#!/bin/bash
set -x

PROJECT_ROOT_DIR=`git rev-parse --show-toplevel`

source ${PROJECT_ROOT_DIR}/bluir_paths.sh

mkdir -p $bluirOutDir

bluirQueryFile=$1
bluirResultsFile=$2
topN=$3

cd ${bluirHome}

#perform retrieval to identify buggy files
$jBLUiR -task='retrieve' \
 -queryFilePath=${bluirQueryFile} \
 -indexLocation=${bluirOutDir}/index \
 -resultPath=${bluirResultsFile} \
 -topN=${topN} \
