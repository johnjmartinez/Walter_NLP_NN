from bug_repository import BugReportContentHandler
import re
import sys
import xml

# run me with:
#   python bluir_analysis.py testRunOut\results.txt SWTBugRepository.xml

class Result():
    def __init__(self, bugReportID, queryID):
        self.bugReportID = bugReportID
        self.queryID = queryID
        self.files = []

    def addFile(self, file, rank, relevance):
        self.files.append((file, int(rank), float(relevance)))

    def getFiles(self):
        return map(lambda x: x[0], self.files)

    def getFilesWithRank(self):
        return map(lambda x: (x[0], x[1]), self.files)

    def __str__(self):
        return "Result for Bug Report %s:\n\t%s" % (self.bugReportID, self.__repr__())

    def __repr__(self):
        return "\n\t".join([str(file) for file in self.files])

def createBugReportResultsMap(resultsFilePath):
    '''
    Example format for result line
    75739 Q0 org.eclipse.swt.ole.win32.Variant.java 1 0.931489 indri
    '''
    resultLinePattern = \
        r'''^(?P<bugReportID>\d+?)\s+?(?P<queryID>\S+?)\s+?(?P<file>\S+?)\s+?(?P<rank>\d+)\s+?(?P<relevance>\d+?\.\d+)\s+?(?P<irMethod>\S+)$'''
    resultLineRE = re.compile(resultLinePattern)

    bugReportResultsMap = {}

    with open(resultsFilePath, 'r') as resultsFile:
        for resultLine in resultsFile:
            match = resultLineRE.match(resultLine)
            if match:
                bugReportID = match.group('bugReportID')

                if bugReportID not in bugReportResultsMap:
                    bugReportResultsMap[bugReportID] = Result(bugReportID, match.group('queryID'))

                bugReportResultsMap[bugReportID].addFile(match.group('file'), match.group('rank'), match.group('relevance'))
            else:
                raise Exception("Unexpected pattern encountered for result line:\n\t%s" % resultLine)

    return bugReportResultsMap

def createBugReportSourceFileMap(bugRepositoryFilePath):
    bugReportParser = xml.sax.make_parser()
    bugReportContentHandler = BugReportContentHandler()
    bugReportParser.setContentHandler(bugReportContentHandler)

    with open(bugRepositoryFilePath, 'r') as bugRepositoryFile:
        bugReportParser.parse(bugRepositoryFile)

    bugReportSourceFileMap = {}
    for (bugReportID, bugReportWords, bugReportFiles) in bugReportContentHandler.bugReportInformation:
        bugReportSourceFileMap[bugReportID] = bugReportFiles

    return bugReportSourceFileMap

class BLUiRAnalysis():
    def __init__(self, bugReportSourceFileMap):
        self.bugReportSourceFileMap = bugReportSourceFileMap

    def calculateRecallAtTopN(self, bugReportResultsMap, N):
        recallAtTopN = 0
        for bugReportID in bugReportResultsMap:
            for sourceFile in bugReportSourceFileMap[bugReportID]:
                if sourceFile in bugReportResultsMap[bugReportID].getFiles()[0:N]:
                    recallAtTopN += 1
                    break
        return recallAtTopN

    def calculateMeanReciprocalRank(self, bugReportResultsMap):
        reciprocalRankSum = 0.0

        for bugReportID in bugReportResultsMap:
            reciprocalRankSum += \
                self.calculateReciprocalRank(bugReportResultsMap[bugReportID], self.bugReportSourceFileMap[bugReportID])

        return reciprocalRankSum / len(bugReportResultsMap)

    def calculateReciprocalRank(self, result, bugReportSourceFiles):
        for (sourceFile, rank) in result.getFilesWithRank():
            if sourceFile in bugReportSourceFiles:
                return (1.0 / rank)

        return 0.0

    def calculateMeanAveragePrecision(self, bugReportResultsMap):
        averagePrecisionSum = 0.0
        for bugReportID in bugReportResultsMap:
            averagePrecisionSum += \
                self.calculateAveragePrecision(bugReportResultsMap[bugReportID], self.bugReportSourceFileMap[bugReportID])
        return averagePrecisionSum / len(bugReportResultsMap)

    def calculateAveragePrecision(self, result, bugReportSourceFiles):
        averagePrecision = 0.0
        numCorrectSourceFiles = 0

        for (sourceFile, rank) in result.getFilesWithRank():
            if sourceFile in bugReportSourceFiles:
                numCorrectSourceFiles += 1
                change = 1.0 / len(bugReportSourceFiles)
            else:
                change = 0.0

            precision = float(numCorrectSourceFiles) / rank
            averagePrecision += (change * precision)
        return averagePrecision

if __name__ == '__main__':
    resultsFilePath = sys.argv[1]
    bugReportResultsMap = createBugReportResultsMap(resultsFilePath)

    bugRepositoryFilePath = sys.argv[2]
    bugReportSourceFileMap = createBugReportSourceFileMap(bugRepositoryFilePath)

    bluirAnalysis = BLUiRAnalysis(bugReportSourceFileMap)

    print "Results File Path: %s" % resultsFilePath
    print "Bug Repository File Path: %s" % bugRepositoryFilePath
    print 
    print "Top 1: %d" % bluirAnalysis.calculateRecallAtTopN(bugReportResultsMap, 1)
    print "Top 5: %d" % bluirAnalysis.calculateRecallAtTopN(bugReportResultsMap, 5)
    print "Top 10: %d" % bluirAnalysis.calculateRecallAtTopN(bugReportResultsMap, 10)
    print "MRR: %f" % bluirAnalysis.calculateMeanReciprocalRank(bugReportResultsMap)
    print "MAP: %f" % bluirAnalysis.calculateMeanAveragePrecision(bugReportResultsMap)
