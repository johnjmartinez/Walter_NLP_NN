import re, xmltodict, json
from os import listdir, makedirs
from os.path import isfile, join, dirname

from tfidf import TFIDF

from global_constants import *


class Document:
    '''This is a document in the sense of a corpus, not in the sense of Indri'''

    def __init__(self, structuredText):
        self.structuredText = {
            CLASS: self._coerceNoneToEmptyString(structuredText[CLASS]),
            METHOD: self._coerceNoneToEmptyString(structuredText[METHOD]),
            IDENT: self._coerceNoneToEmptyString(structuredText[IDENT]),
            COMMENTS: self._coerceNoneToEmptyString(structuredText[COMMENTS])
        }

    def getFlattenedText(self, categories=[CLASS, METHOD, IDENT]):
        ''' By default, we exclude the comments category because it makes learning harder '''
        return "\n".join([self.structuredText[category] for category in categories])

    def getWords(self, categories=[CLASS, METHOD, IDENT], camelCasifyJava=True, filterWords=[]):
        ''' By default, we exclude the comments category because it makes learning harder '''
        words = []
        for category in categories:
            if camelCasifyJava == False or category == COMMENTS: # Don't camelCasifyJava comments
                words.extend(self.structuredText[category].split())
            else:
                words.extend([self._camelCasify(line.split()) for line in self.structuredText[category].split('\n')])

        return filter(lambda x: x and x not in filterWords, words) # filter empty strings and words in filterWords

    def _coerceNoneToEmptyString(self, string):
        return '' if string == None else string

    def _camelCasify(self, wordList):
        if len(wordList) == 0:
            return ''

        elif len(wordList) == 1:
            return wordList[0]

        return wordList[0] + "".join([word.title() for word in wordList[1:]])

def createBugFixedFileMap(bugRepositoryFilePath):
    parsedBugData = xmltodict.parse(open(bugRepositoryFilePath, 'r').read())

    # { bugId (string) : fixedFiles (list of string) }
    bugFixedFileMap = {}
    for bug in parsedBugData['bugrepository']['bug']:
        fixedFiles = bug['fixedFiles']['file']

        if type(fixedFiles) is not list:
            fixedFiles = [fixedFiles]

        bugFixedFileMap[bug['@id']] = fixedFiles

    return bugFixedFileMap

def createBugMap(indriQueryPath):
    parsedIndriQueryData = xmltodict.parse(open(indriQueryPath, "r").read())

    structurePatterns = {
        CLASS: re.compile(r"(\S+)\.\(class\)"),
        METHOD: re.compile(r"(\S+)\.\(method\)"),
        IDENT: re.compile(r"(\S+)\.\(identifier\)"),
        COMMENTS: re.compile(r"(\S+)\.\(comments\)")
    }

    bugMap = {}
    for query in parsedIndriQueryData['parameters']['query']:
        bugMap[query['number']] = \
            Document({ structure : " ".join(pattern.findall(query['text'])) for (structure, pattern) in structurePatterns.iteritems() })

    return bugMap

def createFixedFileMap(indriDocumentsPath):
    indriDocuments = [ file for file in listdir(indriDocumentsPath) if isfile(join(indriDocumentsPath, file)) ]
    indriDocumentStrings = { document : open(join(indriDocumentsPath, document), 'r').read() for document in indriDocuments }
    parsedIndriDocumentData = { document : xmltodict.parse(indriDocumentStrings[document]) for document in indriDocumentStrings }

    # { fixedFileName (string) : Document }
    fixedFileMap = {}
    for documentId in parsedIndriDocumentData:
        indriDocument = parsedIndriDocumentData[documentId]['DOC']
        fixedFile = indriDocument['DOCNO']
        fixedFileMap[fixedFile] = Document(indriDocument['text'])

    return fixedFileMap


def computeFilterWordsUsingTfIdf(documentMap, cutoff=0.0):
    documentWordScores = TFIDF(documentMap).compute()

    return \
        {
            documentName : map(lambda x: x[0], filter(lambda x: x[1] <= cutoff, documentWordScores[documentName].items()))
            for documentName in documentWordScores
        }

def dumpToFileAsJSON(filePath, data):
    with open(filePath, 'w') as outfile:
         json.dump(data, outfile, sort_keys = True, indent = 4, ensure_ascii=False)


if __name__ == "__main__":
    # READ THE GOODNESS


    bugFixedFileMap = createBugFixedFileMap(bugRepositoryFilePath)

    bugMap = createBugMap(indriQueryPath)

    fixedFileMap = createFixedFileMap(indriDocumentsPath)

    BUG_REPORTS_TFIDF_CUTOFF = .001
    FIXED_FILES_TFIDF_CUTOFF = .001

    bugReportFilterWords = computeFilterWordsUsingTfIdf(
        { bugId : bugMap[bugId].getFlattenedText([CLASS]) for bugId in bugMap }, # We only need the words for one structure
        cutoff=BUG_REPORTS_TFIDF_CUTOFF
    )

    fixedFileFilterWords = computeFilterWordsUsingTfIdf(
        { fixedFileName : "\n".join(fixedFileMap[fixedFileName].getWords()) for fixedFileName in fixedFileMap },
        cutoff=BUG_REPORTS_TFIDF_CUTOFF
    )


    dumpToFileAsJSON(bugReportFilterWordsPath, bugReportFilterWords)
    dumpToFileAsJSON(fixedFileFilterWordsPath, fixedFileFilterWords)

    # Check filter words
    '''
    for bugId in bugMap:
        print "Getting words for: %s" % bugId
        bugReport = bugMap[bugId]
        print "--count before filter: %d" % len(bugReport.getWords([CLASS], camelCasifyJava=False))
        print "--count after filter: %d" % len(bugReport.getWords([CLASS], camelCasifyJava=False, filterWords=bugReportFilterWords[bugId]))

    for fixedFileName in fixedFileMap:
        print "Getting words for: %s" % fixedFileName
        fixedFile = fixedFileMap[fixedFileName]
        print "--count before filter: %d" % len(fixedFile.getWords())
        print "--count after filter: %d" % len(fixedFile.getWords(filterWords=fixedFileFilterWords[fixedFileName]))
    '''

    # { structure : [[bagOfWordsList]] }
    bugReportBOWs = []
    fixedFileBOWs = []

    for bugId in bugFixedFileMap:
        for fixedFile in bugFixedFileMap[bugId]:
            bugReportBOWs.append(list(set(bugMap[bugId].getWords(filterWords=bugReportFilterWords[bugId], camelCasifyJava=False))))
            fixedFileBOWs.append(list(set(fixedFileMap[fixedFile].getWords(filterWords=fixedFileFilterWords[fixedFile]))))

    #save as json file

    dumpToFileAsJSON(bugReportBOWsPath, bugReportBOWs)
    dumpToFileAsJSON(fixedFileBOWsPath, fixedFileBOWs)