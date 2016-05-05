import argparse
import ConfigParser
import theanets
import xml

from global_constants import *
import word_mapping
import corpus
import utils
from losses import CrossEntropyLoss # needed to load the network

parser = argparse.ArgumentParser(description='Translates the words in BLUiR\'s generated Indri query according to the word mapping dictated by the given model(s).')
parser.add_argument('-i', '--input-query', help='Path to the BLUiR-generated Indri query XML file')
parser.add_argument('-t', '--translated-query', help='Path to the translated Indri query XML file')
parser.add_argument('-g', '--config', help='Path to script-specific configuration file.')
parser.add_argument('-c', '--confidence-threshold', nargs='+', help='Mapped words with a confidence level less than this value will not be used in the translation.')

args = parser.parse_args()

config = ConfigParser.ConfigParser()
config.read(args.config)

print "Loading models"
structures = [CLASS, METHOD, IDENTIFIER]
structuredModels = {
    structure : theanets.Network.load(utils.addSuffixToPath(config.get('Model', 'ModelPath'), structure))
    for structure in structures
}

print "Creating structured word mappings"
structuredWordMappings = \
    word_mapping.createWordMappingFromContextedModels(
        structuredModels,
        corpus.Corpus.fromFile(config.get('BugReports', 'CorpusPath')),
        corpus.Corpus.fromFile(config.get('FixedFiles', 'CorpusPath'))
    )


print "Translating query..."
for confidenceThreshold in args.confidence_threshold:
    print "...confidence threshold: %s" % confidenceThreshold

    with open(args.input_query, "r") as queryFile:
        wordMapper = word_mapping.WordMapper(structuredWordMappings, float(confidenceThreshold))

        with open(utils.addSuffixToPath(args.translated_query, confidenceThreshold), 'w') as translatedQueryFile:
            queryContentHandler = word_mapping.QueryContentHandler(wordMapper, translatedQueryFile)

            queryParser = xml.sax.make_parser()
            queryParser.setContentHandler(queryContentHandler)

            queryParser.parse(queryFile)
