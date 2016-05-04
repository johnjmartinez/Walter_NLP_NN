from xml.sax.handler import ContentHandler
import json
import time

def normalizeWhitespace(text):
        "Remove redundant whitespace from a string"
        return ' '.join(text.split())

class AutoContentHandler(ContentHandler):
    def startElement(self, name, attrs):
        startElementHandler = getattr(self, "start_" + name, None)
        if callable(startElementHandler):
            startElementHandler(name, attrs)

    def endElement(self, name):
        endElementHandler = getattr(self, "end_" + name, None)
        if callable(endElementHandler):
            endElementHandler(name)

def dumpToJSONFile(filePath, data):
    with open(filePath, 'w') as jsonFile:
        json.dump(data, jsonFile, sort_keys = True, indent = 4, ensure_ascii=False)

def readFromJSONFile(filePath):
    with open(filePath, 'w') as jsonFile:
        return json.load(jsonFile)

def getCurrentTime():
    localtime = time.asctime(time.localtime(time.time()))
    return localtime

def coerceNoneToEmptyString(string):
    return '' if string == None else string

def camelCasify(wordList):
    if len(wordList) == 0:
        return ''

    elif len(wordList) == 1:
        return wordList[0]

    return wordList[0] + "".join([word.title() for word in wordList[1:]])