from graphene import ObjectType, Schema, String, List, Field
from textProcessing.app import addNLPTagsToPlainText #todo move this
from rnnProduction import rnnProduction
from pathlib import Path

ioRoot = Path('E:\\code\\pyNLP\\wt103') #folder with files
ixToVocabPath = ioRoot / 'itos_wt103.pkl'
modelWeightsPath = ioRoot / 'fwd_wt103.h5'
encPath = ioRoot / 'fwd_wt103_enc.h5'
rnn = rnnProduction(ixToVocabPath, modelWeightsPath, encPath)
# todo add these end points
# pairWiseDist = rnn.getPairWiseDistance(vectors)
# tsnePoints = rnn.getTSNE(vectors)
# genText = rnn.getNextWords('cognitive science is important because ')

class Query(ObjectType):
    xmlFromNLP = String(text=String(default_value=""))

    def resolve_xmlFromNLP(self, info, text):
        joinedSents = ' '.join(addNLPTagsToPlainText(text))
        return f"<p>{joinedSents}</p>"

    getRNNVectors = String(strList=List(String))

    def resolve_getRNNVectors(self, info, strList):
        return rnn.getVectorsFromList(strList)


schema = Schema(query=Query)