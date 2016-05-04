#!/bin/bash

classStructureModelPath=analysis_set_1/bow_adadelta_m1_loss001.mod
methodStructureModelPath==analysis_set_1/bow_adadelta_m1_loss001.mod
identifierStructureModelPath==analysis_set_1/bow_adadelta_m1_loss001.mod
commentsStructureModelPath==analysis_set_1/bow_adadelta_m1_loss001.mod
sourceCorpusPath=sourceCorpus.pkl
targetCorpusPath=targetCorpus.pkl
queryPath=testRunOut/query

python translate_query.py \
    -c $classStructureModelPath \
    -m $methodStructureModelPath \
    -i $identifierStructureModelPath \
    -n $commentsStructureModelPath \
    -s $sourceCorpusPath \
    -t $targetCorpusPath \
    -q queryPath