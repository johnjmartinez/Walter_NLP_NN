# gensim modules
from gensim import utils
from gensim import corpora, models, similarities
from gensim.models.doc2vec import LabeledSentence as d2v
from gensim.models import Doc2Vec
import gensim

# numpy
import numpy

# random
from random import shuffle

# classifier
from sklearn.linear_model import LogisticRegression
from sklearn import svm, metrics

from os import listdir, path

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', \
                    level=logging.INFO)

class DocIterator(object):
    def __init__(self, doc_list, labels_list):
       self.labels_list = labels_list
       self.doc_list = doc_list
    def __iter__(self):
        for idx, doc in enumerate(self.doc_list):
            yield d2v(words=doc.split(),tags=[self.labels_list[idx]])


docLabels = [f for f in listdir("./temp_files/")]
data = []
for doc in docLabels:
    f = open("./temp_files/" + doc, 'r')
    data.append(f.read())
    f.close()

it = DocIterator(data, docLabels)

model = Doc2Vec(size=300, window=10, min_count=5, \
                workers=4, alpha=0.025, min_alpha=0.025) # use fixed learning rate
model.build_vocab(it)

for epoch in range(10):
    model.train(it)
    model.alpha -= 0.002 # decrease the learning rate
    model.min_alpha = model.alpha # fix the learning rate, no deca
    model.train(it)

print model.most_similar("most_similar.d2v")
model["raw.d2v"]
