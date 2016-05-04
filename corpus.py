import pickle

class Corpus:

    def __init__(self, contextedBagsOfWords):
        self.contextedBagsOfWords = contextedBagsOfWords
        self.contextedVocabulary = \
            { context : self._makeVocabulary(self.contextedBagsOfWords[context]) for context in self.contextedBagsOfWords }

        self.contextedWordVectors = \
            {
                context : [self.convertToWordVector(bagOfWords, context) for bagOfWords in self.contextedBagsOfWords[context]]
                for context in self.contextedBagsOfWords
            }


    def _makeVocabulary(self, bagsOfWords):
        vocabulary = set()
        for bw in bagsOfWords:
            vocabulary.update(bw)
        return list(vocabulary)

    def convertToWordVector(self, bagOfWords, context):
        return [1 if word in bagOfWords else 0 for word in self.contextedVocabulary[context]]

    def convertFromWordVector(self, wordVector, context):
        # print wordVector
        bagOfWords = []
        for (wordExists, word) in zip(wordVector, self.contextedVocabulary[context]):
            if wordExists:
                bagOfWords.append(word)
        return bagOfWords

    def wordCount(self, context):
        return len(self.contextedVocabulary[context])

    def printToConsole(self):
        for context in self.contextedVocabulary:
            print "Context: %s" % context
            print "--Vocabulary Size: %s" % self.wordCount(context)
            print

    @staticmethod
    def fromFile(filePath):
        with open(filePath, 'r') as corpusFile:
            return pickle.load(corpusFile)

    def toFile(self, filePath):
        with open(filePath, 'w') as corpusFile:
            pickle.dump(self, corpusFile)

