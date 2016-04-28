#from theanets import Autoencoder
from theanets import Network
from theanets.losses import Loss
from os import path

import theano.tensor as TT
import numpy as np
import json, time


class BOWLoss(Loss):
    def __call__(self, outputs):
        output = outputs[self.output_name]
        target = self._target
        xe = target * TT.log(output) + (1 - target) * TT.log(1 - output) # Cross-entropy
        return -xe.sum()

class Corpus:
    def __init__(self, sentences):
        self.sentences = sentences

        bagsOfWords = self.convertToBagsOfWords(self.sentences)
        self.vocabulary = self.makeVocabulary(bagsOfWords)
        self.wordVectors = [self.convertToWordVector(bagOfWords) for bagOfWords in bagsOfWords]

    def convertToBagsOfWords(self, sentences):
        return [sentence.split() for sentence in sentences]

    def makeVocabulary(self, bagsOfWords):
        vocabulary = set()

        for bw in bagsOfWords:
            vocabulary.update(bw)

        return list(vocabulary)

    def convertToWordVector(self, bagOfWords):
        return [1 if word in bagOfWords else 0 for word in self.vocabulary]

    def convertFromWordVector(self, wordVector):
        #print wordVector
        bagOfWords = []
        for (wordExists, word) in zip(wordVector, self.vocabulary):
            if wordExists:
                bagOfWords.append(word)
        return bagOfWords

    def wordCount(self):
        return len(self.vocabulary)

    def printToConsole(self):
        print "Vocabulary: %s" % self.vocabulary
        print
        print "Vocabulary Size: %s" % self.wordCount()
        print "Sentences:\n%s" % self.sentences
        print
        print "Word Vectors:\n%s" % self.wordVectors
        print
        print

def simpleTranslate(sentences, translationMap):
    translatedSentences = []
    for sentence in sentences:
        for (sourceWord, targetWord) in translationMap.iteritems():
            sentence = sentence.replace(sourceWord, targetWord)
        translatedSentences.append(" ".join(sentence.split()))
    return translatedSentences

def getTime():
     localtime = time.asctime( time.localtime(time.time()) )
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

englishCorpus = Corpus(englishSentences)
alieneseSentences = simpleTranslate(englishSentences, englishToAlieneseTranslationMap)
alieneseCorpus = Corpus(alieneseSentences)

englishCorpus[0].printToConsole()
alieneseCorpus[0].printToConsole()

"""


#REAL DATA 
englishCorpus = []
alieneseCorpus = []
field = []
print "Opening map"
with open('query2doc2field_map.txt') as data_file:    
    data = json.load(data_file)

for f in data.keys():
	
	field.append(f)

	print "Creating source nodes corpus for %s"%f
	x=Corpus(data[f].keys())
	englishCorpus.append(x)
	print " .... %s words" % x.wordCount()

	print "Creating target nodes corpus for %s"%f 
	alien = []   
	for val in data[f].values():
		a = ' '.join(list(set(val)))
		alien.append(a)
	y=Corpus(alien)
	alieneseCorpus.append(y)
	print " .... %s words" % y.wordCount()

exit
#HERE GOES NOTHING
ae = []
print "Creating ae model"   
ae[0] = Network(
    [
        englishCorpus[0].wordCount(),
        ((englishCorpus[0].wordCount() + alieneseCorpus[0].wordCount())) / 2,
        (alieneseCorpus[0].wordCount(), 'sigmoid')
    ],
    loss='bowloss'
)
 
modelPath = "./bowloss_nag_mmntm1_loss001_gpu.mod"
# if path.isfile(modelPath):
#	ae.load(modelPath)
# else:
# ae.train([np.asarray(englishCorpus[0].wordVectors), np.asarray(alieneseCorpus[0].wordVectors)], algo='sgd')
#	ae.save(modelPath)

print "Training ae model %s" % modelPath
print " - start time: %s" % getTime()
x=1
target_loss =  0.001
while x > target_loss:
    for train, valid in ae.itertrain([np.asarray(englishCorpus[0].wordVectors,  dtype=np.float32), 
                                      np.asarray(alieneseCorpus[0].wordVectors, dtype=np.float32)], 
                                      algo='nag', momentum=1):
                                    
        if train['loss'] < target_loss: break # NOT RELIABLE ... MAY STOP TRAINING WAY BEFORE TARGET LOSS
    
    print "  time: %s" % getTime()
    print "  training loss: %s" % train['loss']
    print "  validation loss: %s\n" % valid['loss']
    x = train['loss']

print " - stop time: %s\n" % getTime()     
print "Saving ae model"       
ae.save(modelPath)
# for wordVector in englishCorpus[0].wordVectors:
#	print alieneseCorpus[0].convertFromWordVector(ae.predict(np.asarray([wordVector]))[0].tolist())

print "Testing ae model"   
for word in englishCorpus[0].vocabulary: 
    englishWordVector = englishCorpus[0].convertToWordVector([word])
    alienWordVector = ae.predict(np.asarray([englishWordVector], dtype=np.float32))[0]
    # highestProbabilityIndex = np.argmax(alienWordVector)
    sortedIndices = np.argsort(alienWordVector)[::-1]
    print "%s: %s" % (word, np.asarray(alieneseCorpus[0].vocabulary)[sortedIndices[0:2]])
    # print "%s: %s" % (word, alieneseCorpus[0].vocabulary[highestProbabilityIndex])
