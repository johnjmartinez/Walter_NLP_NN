#!/bin/bash
PROJECT_ROOT_DIR=`git rev-parse --show-toplevel`

jBLUiR="java -jar BLUiR.jar"
bluirHome=${PROJECT_ROOT_DIR}/BLUiR
bluirBugRepo=${PROJECT_ROOT_DIR}/SWTBugRepository.xml
bluirSrcRepo=${PROJECT_ROOT_DIR}/swt_src_code
bluirOutDir=${PROJECT_ROOT_DIR}/testRunOut #or whatever you wanna call it