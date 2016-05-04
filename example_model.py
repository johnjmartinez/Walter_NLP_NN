def simpleTranslate(sentences, translationMap):
    translatedSentences = []
    for sentence in sentences:
        for (sourceWord, targetWord) in translationMap.iteritems():
            sentence = sentence.replace(sourceWord, targetWord)
        translatedSentences.append(" ".join(sentence.split()))
    return translatedSentences



"""
englishToAlieneseTranslationMap = {
    'the': '',  # goes away
    'dog': 'dog',
    'ran': 'nar',
    'to': 'ot',
    'store': 'ros te',  # 1 to 2
    'cat': 'tac',
    'is': 'si',
    'dead': 'edad',
    'ate': 'eta',
    'blew up': 'pewbul'  # 2 to 1
}
englishSentences = [
    'the dog ran to the store',
    'the store blew up',
    'the cat blew up the store',
    'the dog ate the cat',
    'the dog blew up the cat',
    'the cat is dead',
    'the dog is the cat',
    'the dog blew up',
    'the store ate the dog',
    'the cat ran to the dog',
    'the store is dead',
    'the dog is dead'
]
sourceCorpus = Corpus(englishSentences)
alieneseSentences = simpleTranslate(englishSentences, englishToAlieneseTranslationMap)
targetCorpus = Corpus(alieneseSentences)
"""