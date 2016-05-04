import xml
import utils

'''
Example
<bugrepository name="SWT">
  <bug id="75739" opendate="2004-10-06 17:02:00" fixdate="2004-10-18 17:40:00">
    <buginformation>
      <summary>Variant has no toString()</summary>
      <description>The Variant class has no toString() and one cannot call getString() in all cases since it throws an Exception if the type is VT_EMPTY. So I suggest: /** * Always returns a String. * &amp;#64;param variant * &amp;#64;return a String */ public static String toString() { if (this.getType() == COM.VT_EMPTY) { return &amp;quot;&amp;quot;; } return this.getString(); } Version 3.1.M2.</description>
    </buginformation>
    <fixedFiles>
      <file>org.eclipse.swt.ole.win32.Variant.java</file>
    </fixedFiles>
  </bug>
</bugrepository>
'''
class BugReportContentHandler(utils.AutoContentHandler):
    def __init__(self):
        self.bugRepositoryName = None
        self.currentBugReportId = None
        self.currentBugReportWords = []
        self.currentFiles = []
        self.bugReportInformation = []
        self.capturingBugInformation = False
        self.capturingFile = False

    def start_bugrepository(self, name, attrs):
        self.bugRepositoryName = utils.normalizeWhitespace(attrs.get("name"))

    def start_bug(self, name, attrs):
        self.currentBugReportId = utils.normalizeWhitespace(attrs.get("id"))

    def start_buginformation(self, name, attrs):
        self.capturingBugInformation = True
        self.currentBugReportWords = []

    def start_summary(self, name, attrs):
        pass

    def start_description(self, name, attrs):
        pass

    def start_fixedFiles(self, name, attrs):
        self.currentFiles = []
        pass

    def start_file(self, name, attrs):
        self.capturingFile = True

    def end_bugrepository(self, name):
        pass
         
    def end_bug(self, name):
        self.bugReportInformation.append((self.currentBugReportId, self.currentBugReportWords, self.currentFiles))

    def end_buginformation(self, name):
        self.capturingBugInformation = False

    def end_summary(self, name):
        pass

    def end_description(self, name):
        pass

    def end_fixedFiles(self, name):
        pass

    def end_file(self, name):
        self.capturingFile = False

    def characters(self, content):
        if self.capturingBugInformation:
            self.currentBugReportWords.extend(self.parseWords(content))
        elif self.capturingFile:
            self.currentFiles.append(utils.normalizeWhitespace(content))

    def parseWords(self, content):
        return content.split()


if __name__ == "__main__":
    bugReportContentHandler = BugReportContentHandler()

    bugReportParser = xml.sax.make_parser()
    bugReportParser.setContentHandler(bugReportContentHandler)
    bugReportParser.parse(open("SWTBugRepository.xml", "r"))


    from pprint import pprint

    pprint(bugReportContentHandler.bugReportInformation)

