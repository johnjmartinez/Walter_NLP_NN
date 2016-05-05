import re, xmltodict, json
from os import listdir, makedirs
from os.path import isfile, join, dirname, splitext
import argparse
import ConfigParser

from global_constants import *
import tfidf
import utils
import corpus
import document

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
        IDENTIFIER: re.compile(r"(\S+)\.\(identifier\)"),
        COMMENTS: re.compile(r"(\S+)\.\(comments\)")
    }

    bugMap = {}
    for query in parsedIndriQueryData['parameters']['query']:
        bugMap[query['number']] = \
            document.Document({ structure : " ".join(pattern.findall(query['text'])) for (structure, pattern) in structurePatterns.iteritems() })

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
        fixedFileMap[fixedFile] = document.Document(indriDocument['text'])

    return fixedFileMap


def computeFilterWordsUsingTfIdf(documentMap, cutoff):
    documentWordScores = tfidf.TFIDF(documentMap).compute()
    return \
        {
            documentName : map(lambda x: x[0], filter(lambda x: x[1] <= cutoff, documentWordScores[documentName].items()))
            for documentName in documentWordScores
        }


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Creates a source and target corpus, filtered by TF/IDF.')
    parser.add_argument('-b', '--bug-repository', help='Path to bug repository XML file.')
    parser.add_argument('-q', '--indri-query', help='Path to Indri query XML file.')
    parser.add_argument('-d', '--indri-documents', help='Path to folder containing Indri document XML files.')
    parser.add_argument('-g', '--config', help='Path to script-specific configuration file.')

    args = parser.parse_args()

    config = ConfigParser.ConfigParser()
    config.read(args.config)

    bugReportsTFIDFCutoff = float(config.get('BugReports', 'TFIDFCutoff'))
    bugReportsFilterWordsSavePath = config.get('BugReports', 'FilterWordsPath')
    bugReportsCorpusSavePath = config.get('BugReports', 'CorpusPath')

    fixedFilesTFIDFCutoff = float(config.get('FixedFiles', 'TFIDFCutoff'))
    fixedFilesFilterWordsSavePath = config.get('FixedFiles', 'FilterWordsPath')
    fixedFilesCorpusSavePath = config.get('FixedFiles', 'CorpusPath')

    # READ THE GOODNESS
    bugFixedFileMap = createBugFixedFileMap(args.bug_repository)
    bugMap = createBugMap(args.indri_query)
    fixedFileMap = createFixedFileMap(args.indri_documents)

    structures = [CLASS, METHOD, IDENTIFIER]

    # { structure : [[bagOfWordsList]] }
    bugReportBOWs = { structure : [] for structure in structures }
    fixedFileBOWs = { structure : [] for structure in structures }

    for structure in structures:

        bugReportFilterWords = computeFilterWordsUsingTfIdf(
            { bugId : bugMap[bugId].getFlattenedText([structure]) for bugId in bugMap }, # We only need the words for one structure
            bugReportsTFIDFCutoff
        )

        fixedFileFilterWords = computeFilterWordsUsingTfIdf(
            { fixedFileName : "\n".join(fixedFileMap[fixedFileName].getWords([structure])) for fixedFileName in fixedFileMap },
            fixedFilesTFIDFCutoff
        )

        utils.dumpToJSONFile(utils.addSuffixToPath(bugReportsFilterWordsSavePath, structure), bugReportFilterWords)
        utils.dumpToJSONFile(utils.addSuffixToPath(fixedFilesFilterWordsSavePath, structure), fixedFileFilterWords)

        for bugId in bugFixedFileMap:
            for fixedFile in bugFixedFileMap[bugId]:
                bugReportBOWs[structure].append(list(set(bugMap[bugId].getWords([structure], filterWords=bugReportFilterWords[bugId], camelCasifyJava=False))))
                fixedFileBOWs[structure].append(list(set(fixedFileMap[fixedFile].getWords([structure], filterWords=fixedFileFilterWords[fixedFile]))))

    print "Creating source corpus from bug reports"
    sourceCorpus = corpus.Corpus(bugReportBOWs)
    sourceCorpus.printToConsole()
    print "Saving source corpus to %s" % bugReportsCorpusSavePath
    sourceCorpus.toFile(bugReportsCorpusSavePath)

    print "Creating target corpus from fixed files"
    targetCorpus = corpus.Corpus(fixedFileBOWs)
    targetCorpus.printToConsole()
    print "Saving target corpus to %s" % fixedFilesCorpusSavePath
    targetCorpus.toFile(fixedFilesCorpusSavePath)

