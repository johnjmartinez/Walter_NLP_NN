from theanets import Network
from os import path
import argparse
import numpy as np
import json
import sys

from losses import CrossEntropyLoss
import corpus
import utils
from global_constants import *

parser = argparse.ArgumentParser(description='Creates or analyzes a bag-of-words auto encoder model that represents associations between words in bug reports and words in fixed source code files.')
parser.add_argument('command', choices=['create', 'analyze'], help='Path to the Theanets model')
parser.add_argument('-m', '--model', help='Path to the Theanets model')
parser.add_argument('-s', '--source-corpus', help='Path to the pickled Corpus object for the source corpus (the bug reports)')
parser.add_argument('-t', '--target-corpus', help='Path to the pickled Corpus object for the target corpus (the fixed source code files)')

args = parser.parse_args()

print "Loading source corpus (bug reports)"
sourceCorpus = Corpus.fromFile(args.source_corpus)
print " .... %s words" % sourceCorpus.wordCount()


print "Loading target corpus (fixed files)"
targetCorpus = Corpus.fromFile(args.target_corpus)
print " .... %s words\n" % targetCorpus.wordCount()

#print "Number of training instances: %d" % len(bugReportSentences)

if args.command == "create":
    print "Creating model %s" % args.model_path
    ae = \
        Network(
            [
                sourceCorpus.wordCount(),
                int(((sourceCorpus.wordCount() + targetCorpus.wordCount())) * 0.05),
                (targetCorpus.wordCount(), 'sigmoid')
            ],
            loss='crossentropyloss'
        )

    print "Training model %s" % args.model_path
    print " - start time: %s\n" % getCurrentTime()

    data = [np.asarray(sourceCorpus.wordVectors, dtype=np.float32), np.asarray(targetCorpus.wordVectors, dtype=np.float32)]

    for train, valid in ae.itertrain(data, algo='adadelta', validate_every=1, patience=5):
        print "  time: %s" % getCurrentTime()
        print "  training loss: %s" % train['loss']
        print "  validation loss: %s" % valid['loss']

    print " - stop time: %s" % getCurrentTime()
    print "Saving model %s" % args.model_path
    ae.save(args.model_path)

elif args.command == "analyze":
    print "Loading model %s" % args.model_path
    ae = Network.load(args.model_path)

    for word in sourceCorpus.vocabulary:
        sourceWordVector = sourceCorpus.convertToWordVector([word])
        targetWordVector = ae.predict(np.asarray([sourceWordVector], dtype=np.float32))[0]
        sortedIndices = np.argsort(targetWordVector)[::-1]

        mappedWords = zip(np.asarray(targetCorpus.vocabulary)[sortedIndices[0:5]], targetWordVector[sortedIndices[0:5]])
        print "%s: %s" % (word, mappedWords)
else:
    pass # handled by argparse