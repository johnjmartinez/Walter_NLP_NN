import argparse
import ConfigParser
from theanets import Network
import numpy as np

from losses import CrossEntropyLoss
import corpus
import utils
from global_constants import *

parser = argparse.ArgumentParser(description='Creates a bag-of-words auto encoder model that represents associations between words in bug reports and words in fixed source code files.')
parser.add_argument('command', choices=['create', 'analyze'], help='Path to script-specific configuration file.')
parser.add_argument('-s', '--structure', help='The structure to analyze (applies only when command=analyze).')
parser.add_argument('-n', '--top-n', help='The top N words to display in the analysis (applies only when command=analyze).')
parser.add_argument('-g', '--config', help='Path to script-specific configuration file.')

args = parser.parse_args()

config = ConfigParser.ConfigParser()
config.read(args.config)

print "Loading source corpus (bug reports)"
sourceCorpus = corpus.Corpus.fromFile(config.get('BugReports', 'CorpusPath'))
sourceCorpus.printToConsole()


print "Loading target corpus (fixed files)"
targetCorpus = corpus.Corpus.fromFile(config.get('FixedFiles', 'CorpusPath'))
targetCorpus.printToConsole()

#print "Number of training instances: %d" % len(bugReportSentences)

if args.command == "create":
    structures = [CLASS, METHOD, IDENTIFIER]

    for structure in structures:
        modelSavePath = utils.addSuffixToPath(config.get('Model', 'ModelPath'), structure)

        print "Creating model %s" % modelSavePath
        model = \
            Network(
                [
                    sourceCorpus.wordCount(structure),
                    int(((sourceCorpus.wordCount(structure) + targetCorpus.wordCount(structure))) * float(config.get('Model', 'HiddenLayerSizeProportion'))),
                    (targetCorpus.wordCount(structure), 'sigmoid')
                ],
                loss='crossentropyloss' )

        print "Training model %s" % modelSavePath
        print " - start time: %s\n" % utils.getCurrentTime()

        data = [
            np.asarray(sourceCorpus.getWordVectors(structure), dtype=np.float32),
            np.asarray(targetCorpus.getWordVectors(structure), dtype=np.float32)
        ]

        for train, valid in model.itertrain(data, algo='adadelta', validate_every=1, patience=5):
            print "  time: %s" % utils.getCurrentTime()
            print "  training loss: %s" % train['loss']
            print "  validation loss: %s" % valid['loss']

        print " - stop time: %s" % utils.getCurrentTime()
        print "Saving model %s" % modelSavePath
        model.save(modelSavePath)

elif args.command == "analyze":
    structure = args.structure
    modelLoadPath = utils.addSuffixToPath(config.get('Model', 'ModelPath'), structure)
    print "Loading model %s" % modelLoadPath
    model = Network.load(modelLoadPath)

    for word in sourceCorpus.getVocabulary(structure):
        sourceWordVector = sourceCorpus.convertToWordVector([word], structure)
        targetWordVector = model.predict(np.asarray([sourceWordVector], dtype=np.float32))[0]
        topNIndices = np.argsort(targetWordVector)[::-1][0:int(args.top_n)]

        mappedWords = zip(np.asarray(targetCorpus.getVocabulary(structure))[topNIndices], targetWordVector[topNIndices])
        print "%s: %s" % (word, mappedWords)
else:
    pass # handled by argparse