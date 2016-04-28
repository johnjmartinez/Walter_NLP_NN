from collections import namedtuple

class BugReportWordMapper:
    def __init__(self):
        self.wordMappingsInContext = {}

    def addWordMapping(self, wordMapping, context):
        self.wordMappingsInContext[context] = wordMapping

    def mapWord(self, word, context, confidenceThreshold):
        return map(lambda x: x.word, filter(lambda x: x.confidence > confidenceThreshold, self.wordMappingsInContext[context][word]))


Word = namedtuple('WordWithConfidence', ['word', 'confidence'])

if __name__ == "__main__":

    # John provides ...
    wordMapping_normalContext = {
        "cat": [Word("mouse", 0.9), Word("hairball", 0.4), Word("bird", 0.7)],
        "dog": [Word("bone", .99), Word("hammer", 0.01), Word("meat", 0.8), Word("bath", 0.4)],
        "cow": [Word("spot", .79), Word("milk", 1.0)]
    }

    wordMapping_weirdContext = {
        "cat": [Word("planet", 0.3), Word("coin", 0.43), Word("arrow", 0.92)],
        "dog": [Word("fork", .95), Word("foil", 0.51)],
        "cow": [Word("hair", .43), Word("dirt", 0.02), Word("bottle", 0.74), Word("light", 0.24)]
    }

    # Vince provides ...
    wordMapper = BugReportWordMapper()
    wordMapper.addWordMapping(wordMapping_normalContext, "normal")
    wordMapper.addWordMapping(wordMapping_weirdContext, "weird")

    print wordMapper.mapWord("cat", "normal", 0.75)
    print wordMapper.mapWord("dog", "normal", 0.75)
    print wordMapper.mapWord("cow", "normal", 0.75)

    print wordMapper.mapWord("cat", "weird", 0.48)
    print wordMapper.mapWord("dog", "weird", 0.48)
    print wordMapper.mapWord("cow", "weird", 0.48)