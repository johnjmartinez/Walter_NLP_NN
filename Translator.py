
# coding: utf-8

# In[64]:

import xml
from xml.sax.handler import ContentHandler
import xml.etree.cElementTree as ET
from word_mapper import BugReportWordMapper
from collections import namedtuple

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
#LEFT IN ALL THE CODE THAT CLAYTON HAD UPLOADED TO GITHUB, MAYBE THE CODE HERE CAN BE ALTERED TO FACILITATE XML CREATION SINCE IT IS EVENT BASED
class BugReportContentHandler(AutoContentHandler):
    def __init__(self):
        #elf.bugRepositoryName = None
        self.currentBugReportId = None
        self.currentBugReportWords = []
        #elf.currentFiles = []
        self.bugReportInformation = []
        self.capturingBugInformation = False
        self.capturingFile = False

#   def start_bugrepository(self, name, attrs):
#       self.bugRepositoryName = normalizeWhitespace(attrs.get("name"))

#    def start_bug(self, name, attrs):
#        self.currentBugReportId = normalizeWhitespace(attrs.get("id"))

#    def start_buginformation(self, name, attrs):
#        self.capturingBugInformation = True
#        self.currentBugReportWords = []

    def start_query(self, name, attrs):
        self.capturingBugInformation = True
        self.currentBugReportWords = []

#    def start_summary(self, name, attrs):
#        pass

#    def start_description(self, name, attrs):
#        pass

    def start_text(self, name, attrs):
        pass

#    def start_fixedFiles(self, name, attrs):
#        self.currentFiles = []
#       pass

#    def start_file(self, name, attrs):
#        self.capturingFile = True
        

#    def end_bugrepository(self, name):
#        pass
         
#    def end_bug(self, name):
#        self.bugReportInformation.append((self.currentBugReportId, self.currentBugReportWords, self.currentFiles))

#    def end_buginformation(self, name):
#        self.capturingBugInformation = False
        
    def end_query(self, name):
        self.bugReportInformation.append((self.currentBugReportWords))
        self.capturingBugInformation = False

#    def end_summary(self, name):
#        pass

#    def end_description(self, name):
#        pass

    def end_text(self, name):
        pass
#    def end_fixedFiles(self, name):
#        pass

#    def end_file(self, name):
#        self.capturingFile = False

    def characters(self, content):
        if self.capturingBugInformation:
            self.currentBugReportWords.extend(self.parseWords(content))
        elif self.capturingFile:
            self.currentFiles.append(normalizeWhitespace(content))

    def parseWords(self, content):
        return content.split()


if __name__ == "__main__":
    bugReportContentHandler = BugReportContentHandler()

    bugReportParser = xml.sax.make_parser()
    bugReportParser.setContentHandler(bugReportContentHandler)
    bugReportParser.parse(open("testRunOut/query.xml", "r"))


    from pprint import pprint

#    pprint(bugReportContentHandler.bugReportInformation[0])
#    print bugReportContentHandler.bugReportInformation[0]
    
#Use a parameter that has a threshold


# In[65]:

###THIS WAS A FIRST ATTEMPT TO MAINTAIN A LIST FORMAT, BUT DIDN'T WORK WELL. LEAVING IT HERE JUST IN CASE IT SPURS IDEAS
#parameters = ET.Element("parameters")
#query = ET.SubElement(parameters, "query")
#ET.SubElement(query, "number").text = bugReportContentHandler.bugReportInformation[0][0]
#matchingClass = bugReportContentHandler.bugReportInformation

#for i in range(len(bugReportContentHandler.bugReportInformation)):
#    matchingClass[i] = (filter(lambda x: '.(class)' in x, bugReportContentHandler.bugReportInformation[i]))
    
#ET.SubElement(query, "text").text = matchingClass[0][0]
#tree = ET.ElementTree(parameters)
#tree.write("QueryOutput.xml")


# In[66]:

parameters = ET.Element("parameters") #XML CODE, ROOT
query = ET.SubElement(parameters, "query") #XML CODE, SUB ELEMENT
ET.SubElement(query, "number").text = bugReportContentHandler.bugReportInformation[0][0] #XML CODE, SUB SUB ELEMENT
matchingClass = [] #INITIALIZE LISTS
matchingMethod = []
matchingID = []

for i in range(len(bugReportContentHandler.bugReportInformation)): #PARSING INFO FROM XML INTO LISTS
    matchingClass.extend((filter(lambda x: '.(class)' in x, bugReportContentHandler.bugReportInformation[i])))
    matchingMethod.extend((filter(lambda x: '.(method)' in x, bugReportContentHandler.bugReportInformation[i])))
    matchingID.extend((filter(lambda x: '.(identifier)' in x, bugReportContentHandler.bugReportInformation[i])))
    
matchingClassString = ', '.join(matchingClass) #CREATING STRINGS FOR INPUT BACK INTO XML (MIGHT NEED MORE WORK LIKE INCLUDING WEIGHT)
matchingMethodString = ', '.join(matchingMethod)
matchingIDString = ', '.join(matchingID)

matchingClassStringStrip = matchingClassString.replace(".(class)", "") #STRIPPED IRRELEVANT SEARCH TERM PORTION FROM ALL WORDS
matchingMethodStringStrip = matchingMethodString.replace(".(method)", "")
matchingIDStringStrip = matchingIDString.replace(".(identifier)", "")

ET.SubElement(query, "text").text = matchingIDString #XML CODE, SUB SUB ELEMENT (note: set to identifiers so you can see how it works)
tree = ET.ElementTree(parameters)
tree.write("QueryOutput.xml")


# In[67]:

Word = namedtuple('WordWithConfidence', ['word', 'confidence']) #IMPORTED INSTANCE OF CLAYTON'S CODE TO TEST FUNCTIONALITY

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


# In[68]:

matchingClassSplit = matchingClassStringStrip.split(matchingClassStringStrip.replace(",", " ")) #CREATED LIST FROM STRING AGAIN
matchingMethodSplit = matchingMethodStringStrip.split(matchingMethodStringStrip.replace(",", " "))
matchingIDSplit = matchingIDStringStrip.split(matchingIDStringStrip.replace(",", " "))

testList = ['cat', 'dog', 'cow'] #TEST OF CLAYTON CODE ITERATING OVER A FOR LOOP
print [x.encode('ascii') for x in testList]
for l in range(len(testList)):
    print wordMapper.mapWord(testList[l], "normal", 0.75) #REPLACE WITH MAPPED FILE AND LIST


# In[69]:

"""NOTES: I left a lot of variables here b/c creating the XML might benefit from one of these, they're described below
matchingClass and others are raw bucketed data (lists) ie. they still have .(class) and etc.
matchingClassString and others are strings of bucketed data (not lists) because XML creation above was easier with strings
matchingClassStringStrip and others are string that have been stripped of irrelevant words
matchingClassSplit and others are lists of bucketed data that has been stripped to just words for mapping purposes
I tested Clayton's code and with a test list, and iterating over the list works, it just needs a proper mapping file

Concerns: the text is unicode, not sure if this will break the wordmapper portion, but it can be encoded to ascii or whatever easily
The last part to do was reprinting the XML portion, so I have basic XML set up, but I can't figure out a way to modify a tagged
area without creating a new field, maybe using the SAX events above can help?
The XML is easiest to create with a string, at least it is with my code above, if there's an implementation with a list, then 
that might be easier"""


# In[ ]:



