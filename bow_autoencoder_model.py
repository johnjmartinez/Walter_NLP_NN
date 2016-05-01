from theanets import Network
from theanets.losses import Loss
from os import path

import theano.tensor as TT
import numpy as np
import json
import time
import sys

from corpus import Corpus
from global_constants import *

class BOWLoss(Loss):

    def __call__(self, outputs):
        output = outputs[self.output_name]
        target = self._target
        xe = target * TT.log(output) + (1 - target) * \
            TT.log(1 - output)  # Cross-entropy
        return -xe.sum()

def simpleTranslate(sentences, translationMap):
    translatedSentences = []
    for sentence in sentences:
        for (sourceWord, targetWord) in translationMap.iteritems():
            sentence = sentence.replace(sourceWord, targetWord)
        translatedSentences.append(" ".join(sentence.split()))
    return translatedSentences

def getTime():
    localtime = time.asctime(time.localtime(time.time()))
    return localtime

"""
englishToAlieneseTranslationMap = {
    'the': '',  # goes away
    'dog': 'dog',
    'ran': 'nar',
    'to': 'ot',
    'store': 'ros te',  # 1 to 2
    'cat': 'tac',
    'is': 'si',
    'dead': 'edad',
    'ate': 'eta',
    'blew up': 'pewbul'  # 2 to 1
}
englishSentences = [
    'the dog ran to the store',
    'the store blew up',
    'the cat blew up the store',
    'the dog ate the cat',
    'the dog blew up the cat',
    'the cat is dead',
    'the dog is the cat',
    'the dog blew up',
    'the store ate the dog',
    'the cat ran to the dog',
    'the store is dead',
    'the dog is dead'
]
sourceCorpus = Corpus(englishSentences)
alieneseSentences = simpleTranslate(englishSentences, englishToAlieneseTranslationMap)
targetCorpus = Corpus(alieneseSentences)
"""

# Parse command-line args
usage = "USAGE: [create | analyze] modelPath"
if len(sys.argv) >= 3:
    command = sys.argv[1]
    modelPath = sys.argv[2]
else:
    print usage
    sys.exit(1)

# Load bags-of-words and create corpuses
print "Loading bags-of-words for bug reports"

with open(bugReportBOWsPath) as data_file:
    bugReportSentences = json.load(data_file)

print "Creating source corpus from bug reports"
sourceCorpus = Corpus(bugReportSentences, True)
print " .... %s words" % sourceCorpus.wordCount()

print "Loading bags-of-words for fixed files"

with open(fixedFileBOWsPath) as data_file:
    fixedFileSentences = json.load(data_file)

print "Creating target corpus from fixed files"
targetCorpus = Corpus(fixedFileSentences, True)
print " .... %s words\n" % targetCorpus.wordCount()

print "Number of training instances: %d" % len(bugReportSentences)

if command == "create":
        print "Creating model %s" % modelPath
        ae = \
            Network(
                [
                    sourceCorpus.wordCount(),
                    int(((sourceCorpus.wordCount() + targetCorpus.wordCount())) * 0.05),
                    (targetCorpus.wordCount(), 'sigmoid')
                ], 
                loss='bowloss'
            )

        print "Training model %s" % modelPath
        print " - start time: %s\n" % getTime()

        data = [np.asarray(sourceCorpus.wordVectors, dtype=np.float32), np.asarray(targetCorpus.wordVectors, dtype=np.float32)]

        for train, valid in ae.itertrain(data, algo='adadelta', validate_every=1, patience=5):
            print "  time: %s" % getTime()
            print "  training loss: %s" % train['loss']
            print "  validation loss: %s" % valid['loss']

        print " - stop time: %s" % getTime()
        print "Saving model %s" % modelPath
        ae.save(modelPath)

elif command == "analyze":
    print "Loading model %s" % modelPath
    ae = Network.load(modelPath)

    for word in sourceCorpus.vocabulary:
        sourceWordVector = sourceCorpus.convertToWordVector([word])
        targetWordVector = ae.predict(np.asarray([sourceWordVector], dtype=np.float32))[0]
        sortedIndices = np.argsort(targetWordVector)[::-1]

        mappedWords = zip(np.asarray(targetCorpus.vocabulary)[sortedIndices[0:5]], targetWordVector[sortedIndices[0:5]])
        print "%s: %s" % (word, filter(lambda x: x[1] > 0.75, mappedWords))
else:
    print "Unknown command: %s" % command
    print usage
    sys.exit(1)
