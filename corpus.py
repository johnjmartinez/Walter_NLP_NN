
class Corpus:

    def __init__(self, sentences, alreadyUsingBagsOfWords=False):
        self.sentences = sentences

        if alreadyUsingBagsOfWords:
            bagsOfWords = sentences
        else:
            bagsOfWords = self.convertToBagsOfWords(self.sentences)

        self.vocabulary = self.makeVocabulary(bagsOfWords)
        self.wordVectors = [self.convertToWordVector(
            bagOfWords) for bagOfWords in bagsOfWords]

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
        # print wordVector
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

