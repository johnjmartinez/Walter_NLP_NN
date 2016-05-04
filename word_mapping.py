from collections import namedtuple
import sys
import xml
import utils
import re

Word = namedtuple('WordWithConfidence', ['word', 'confidence'])

class QueryContentHandler(utils.AutoContentHandler):
    '''
    Example XML
    <parameters>
        <query>
            <number>75739</number>
            <text> #weight(1.0 variant.(class) 1.0 has.(class) 1.0 string.(class)) </text>
        </query>
    </parameters>
    '''
    queryWordPattern = r"\d+\.\d+\s+(.+?)\.\((.+?)\)"

    def __init__(self, wordMapper, confidenceThreshold):
        self.bugRepositoryName = None
        self.currentBugReportId = None
        self.currentBugReportWords = []
        self.currentFiles = []
        self.bugReportInformation = []
        self.lastTag = None
        self.wordMapper = wordMapper
        self.confidenceThreshold = confidenceThreshold

    def start_parameters(self, name, attrs):
        sys.stdout.write("<parameters>\n")

    def start_query(self, name, attrs):
        sys.stdout.write("\t<query>\n")

    def start_number(self, name, attrs):
        self.lastTag = name
        sys.stdout.write("\t\t<number>")

    def start_text(self, name, attrs):
        self.lastTag = name
        sys.stdout.write("\t\t<text> #weight(")

    def end_parameters(self, name):
        sys.stdout.write("</parameters>\n")

    def end_query(self, name):
        sys.stdout.write("\t</query>\n")

    def end_number(self, name):
        sys.stdout.write("</number>\n")

    def end_text(self, name):
        sys.stdout.write(") </text>\n")

    def characters(self, content):
        if self.lastTag == "number":
            sys.stdout.write(content)
        elif self.lastTag == "text":
            sys.stdout.write(self.mapWords(content))

    def mapWords(self, wordContent):
        return \
            " ".join(
                [
                    "1.0 %s.(%s)" % (word, match.group(2))
                    for match in re.finditer(QueryContentHandler.queryWordPattern, wordContent)
                    for word in self.wordMapper.mapWord(match.group(1), match.group(2), self.confidenceThreshold)
                ]
            )

class WordMapper:
    def __init__(self, wordMappingsInContext):
        self.wordMappingsInContext = wordMappingsInContext

    def mapWord(self, word, context, confidenceThreshold):
        return [word] if word not in self.wordMappingsInContext[context] else \
            map(
                lambda x: x.word,
                filter(lambda x: x.confidence > confidenceThreshold, self.wordMappingsInContext[context][word])
            )

def createWordMappingFromModel(contextToWordModelMap, sourceCorpus, targetCorpus):
    wordMapping = { context : {} for context in contextToWordModelMap }

    for context in contextToWordModelMap:
        for sourceWord in sourceCorpus.vocabulary:
            sourceWordVector = sourceCorpus.convertToWordVector([sourceWord])
            targetWordVector = ae.predict(np.asarray([sourceWordVector], dtype=np.float32))[0]
            sortedIndices = np.argsort(targetWordVector)[::-1] # high confidence to low confidence

            targetWords = map(lambda x: Word(x), zip(np.asarray(targetCorpus.vocabulary)[sortedIndices], targetWordVector[sortedIndices]))
            wordMapping[context][sourceWord] = targetWords

    return wordMapping

if __name__ == "__main__":
    # Example code

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
    wordMapper = WordMapper(
        { "normal": wordMapping_normalContext, "weird": wordMapping_weirdContext }
    )

    print wordMapper.mapWord("cat", "normal", 0.75)
    print wordMapper.mapWord("dog", "normal", 0.75)
    print wordMapper.mapWord("cow", "normal", 0.75)

    print wordMapper.mapWord("cat", "weird", 0.48)
    print wordMapper.mapWord("dog", "weird", 0.48)
    print wordMapper.mapWord("cow", "weird", 0.48)

