bugRepositoryFilePath = "SWTBugRepository.xml"
indriQueryPath = "testRunOut/query"
indriDocumentsPath = "testRunOut/docs/"

bugReportFilterWordsPath = "modelData/bug_report_filter_words.txt"
fixedFileFilterWordsPath = "modelData/fixed_file_filter_words.txt"

bugReportBOWsPath = "modelData/bug_report_bows.txt"
fixedFileBOWsPath = "modelData/fixed_file_bows.txt"


globals()['CLASS'] = 'class'
globals()['METHOD'] = 'method'
globals()['IDENT'] = 'identifier'
globals()['COMMENTS'] = 'comments'

try:
    makedirs("modelData")
except:
    pass