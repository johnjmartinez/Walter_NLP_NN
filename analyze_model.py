import argparse
from theanets import Network
import numpy as np

from losses import CrossEntropyLoss
import corpus
import utils
from global_constants import *

parser = argparse.ArgumentParser(description='Analyzes a bag-of-words auto encoder model that represents associations between words in bug reports and words in fixed source code files.')
parser.add_argument('-g', '--config', help='Path to script-specific configuration file.')

args = parser.parse_args()

print "Loading source corpus (bug reports)"
sourceCorpus = corpus.Corpus.fromFile(config.get('BugReports', 'CorpusLoadPath'))
sourceCorpus.printToConsole()


print "Loading target corpus (fixed files)"
targetCorpus = corpus.Corpus.fromFile(config.get('FixedFiles', 'CorpusLoadPath'))
targetCorpus.printToConsole()

#print "Number of training instances: %d" % len(bugReportSentences)

modelLoadPath = args.model_load_path

