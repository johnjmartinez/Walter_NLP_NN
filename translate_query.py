import argparse
import pickle
import theanets

import global_constants
import word_mapping
import corpus
from losses import CrossEntropyLoss

parser = argparse.ArgumentParser(description='Translates the words in BLUiR\'s generated Indri query according to the word mapping dictated by the given model(s).')
parser.add_argument('-c', '--class-structure-model', help='Path to the Theanets model corresponding to the class structure in BLUiR')
parser.add_argument('-m', '--method-structure-model', help='Path to the Theanets model corresponding to the method structure in BLUiR')
parser.add_argument('-i', '--identifier-structure-model', help='Path to the Theanets model corresponding to the identifier class structure in BLUiR')
parser.add_argument('-n', '--comments-structure-model', help='Path to the Theanets model corresponding to the comments structure in BLUiR')
parser.add_argument('-s', '--source-corpus', help='Path to the pickled Corpus object for the source corpus (the bug reports)')
parser.add_argument('-t', '--target-corpus', help='Path to the pickled Corpus object for the target corpus (the fixed source code files)')
parser.add_argument('-q', '--query', help='Path to the BLUiR-generated Indri query XML file')

args = parser.parse_args()

structuredModels = {
    CLASS: theanets.Network.load(args.class_structure_model),
    METHOD: theanets.Network.load(args.method_structure_model),
    IDENTIFIER: theanets.Network.load(args.identifier_structure_model),
    COMMENTS: theanets.Network.load(args.comments_structure_model)
}

structuredWordMappings = {
   structure : word_mapping.createWordMappingFromModel(structuredModels[structure], sourceCorpus, targetCorpus)
   for structure in structuredModels
}

sourceCorpus = corpus.Corpus.fromFile(args.source_corpus)
targetCorpus = corpus.Corpus.fromFile(args.target_corpus)

wordMapper = word_mapping.WordMapper(structuredWordMappings, sourceCorpus, targetCorpus)

queryContentHandler = word_mapping.QueryContentHandler(wordMapper)

queryParser = xml.sax.make_parser()
queryParser.setContentHandler(queryContentHandler)

with open(args.query, "r") as queryFile:
    queryParser.parse(queryFile) # this will simultaneously parse and print the translated query to stdout, so capture it with redirection