from global_constants import *
import utils

class Document:
    '''This is a document in the sense of a corpus, not in the sense of Indri'''

    def __init__(self, structuredText):
        self.structuredText = {
            CLASS: utils.coerceNoneToEmptyString(structuredText[CLASS]),
            METHOD: utils.coerceNoneToEmptyString(structuredText[METHOD]),
            IDENTIFIER: utils.coerceNoneToEmptyString(structuredText[IDENTIFIER]),
            COMMENTS: utils.coerceNoneToEmptyString(structuredText[COMMENTS])
        }

    def getFlattenedText(self, categories=[CLASS, METHOD, IDENTIFIER]):
        ''' By default, we exclude the comments category because it makes learning harder '''
        return "\n".join([self.structuredText[category] for category in categories])

    def getWords(self, categories=[CLASS, METHOD, IDENTIFIER], camelCasifyJava=True, filterWords=[]):
        ''' By default, we exclude the comments category because it makes learning harder '''
        words = []
        for category in categories:
            if camelCasifyJava == False or category == COMMENTS: # Don't camelCasifyJava comments
                words.extend(self.structuredText[category].split())
            else:
                words.extend([utils.camelCasify(line.split()) for line in self.structuredText[category].split('\n')])

        return filter(lambda x: x and x not in filterWords, words) # filter empty strings and words in filterWords

