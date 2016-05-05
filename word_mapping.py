from collections import namedtuple
import sys
import xml
import utils
import re
import numpy as np

Word = namedtuple('Word', ['word', 'confidence'])

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

    def __init__(self, wordMapper, translatedQueryFile):
        self.lastTag = None
        self.wordMapper = wordMapper
        self.translatedQueryFile = translatedQueryFile

    def start_parameters(self, name, attrs):
        self.translatedQueryFile.write("<parameters>\n")

    def start_query(self, name, attrs):
        self.translatedQueryFile.write("\t<query>\n")

    def start_number(self, name, attrs):
        self.lastTag = name
        self.translatedQueryFile.write("\t\t<number>")

    def start_text(self, name, attrs):
        self.lastTag = name
        self.translatedQueryFile.write("\t\t<text> #weight(")

    def end_parameters(self, name):
        self.translatedQueryFile.write("</parameters>\n")

    def end_query(self, name):
        self.translatedQueryFile.write("\t</query>\n")

    def end_number(self, name):
        self.translatedQueryFile.write("</number>\n")

    def end_text(self, name):
        self.translatedQueryFile.write(") </text>\n")

    def characters(self, content):
        if self.lastTag == "number":
            self.translatedQueryFile.write(content)
        elif self.lastTag == "text":
            self.mapWords(content)

    def mapWords(self, wordContent):
        for match in re.finditer(QueryContentHandler.queryWordPattern, wordContent):
            sourceWord = match.group(1)
            context = match.group(2)

            self.translatedQueryFile.write("1.0 %s.(%s) " % (sourceWord, context))

            for targetWord in self.wordMapper.mapWord(sourceWord, context):
                self.translatedQueryFile.write("1.0 %s.(%s) " % (targetWord, context))

class WordMapper:
    def __init__(self, contextedWordMappings, confidenceThreshold):
        self.contextedWordMappings = {}
        for context in contextedWordMappings:
            self.contextedWordMappings[context] = {}

            for sourceWord in contextedWordMappings[context]:
                self.contextedWordMappings[context][sourceWord] = []
                for (targetWord, confidence) in contextedWordMappings[context][sourceWord]:
                    if confidence >= confidenceThreshold:
                        self.contextedWordMappings[context][sourceWord].append(targetWord)
                    else:
                        break # we assume the input word mappings are sorted by confidence

    def mapWord(self, word, context):
        if not (context in self.contextedWordMappings and word in self.contextedWordMappings[context]):
            return []
        else:
            return self.contextedWordMappings[context][word]

def createWordMappingFromContextedModels(contextedWordModels, sourceCorpus, targetCorpus):
    wordMapping = { context : {} for context in contextedWordModels }

    for context in contextedWordModels:
        for sourceWord in sourceCorpus.getVocabulary(context):
            sourceWordVector = sourceCorpus.convertToWordVector([sourceWord], context)
            targetWordVector = contextedWordModels[context].predict(np.asarray([sourceWordVector], dtype=np.float32))[0]
            sortedIndices = np.argsort(targetWordVector)[::-1] # high confidence to low confidence

            targetWords = map(lambda x: Word(x[0], x[1]), zip(np.asarray(targetCorpus.getVocabulary(context))[sortedIndices], targetWordVector[sortedIndices]))
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

