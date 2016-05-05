#!/bin/bash
set -x

PROJECT_ROOT_DIR=`git rev-parse --show-toplevel`

source ${PROJECT_ROOT_DIR}/scripts/bluir_paths.sh

mkdir -p $bluirOutDir

# Because of BLUiR's quirks with the current working directory, the files passed in are expected to be
# relative to the root of the project.
bluirQueryFile=$PROJECT_ROOT_DIR/$1
bluirResultsFile=$PROJECT_ROOT_DIR/$2
topN=$3

cd ${bluirHome}

#perform retrieval to identify buggy files
$jBLUiR -task='retrieve' \
 -queryFilePath=${bluirQueryFile} \
 -indexLocation=${bluirOutDir}/index \
 -resultPath=${bluirResultsFile} \
 -topN=${topN} \

# Example Usage
# for file in `ls translated_queries`; do ./scripts/run_bluir_retrieval.sh translated_queries/$file results/${${file/translated_query/results}/xml/txt} 1000000; done