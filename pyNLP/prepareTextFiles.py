# Extract, transform, and load
import csv, json
from os import path
import dask.bag as bag # sort of a parallel unordered pandas dataframe
from dask.distributed import Client
import dask
from os import listdir
from operator import itemgetter
import pandas as pd
from textUtils import wt103RegexFixes
from fastai.text import *

debugging = 0 #e.g. using ipython
client = Client(processes=False, threads_per_worker=1 if debugging else 4,
                n_workers=1, memory_limit='4GB')

articleProps = ["title", "venue", "entities", "year", "paperAbstract" ]

# todo put in corpus dir
ioRoot = 'E:\\code\\pyNLP\\textProcessing\\corpus-2018-05-03'
ioPaths = {
    'corpusAllGlob':    path.join(ioRoot, "txt", "s2-corpus-*.txt"),
    'corpusFirstFile':  path.join(ioRoot, "txt", "s2-corpus-01.txt"),
    'filteredDir':     path.join(ioRoot, "filtered"),
    'filteredJSONGlob': path.join(ioRoot, "filtered", "venueFiltered-*.json"),
    'cscwGlob': path.join(ioRoot,"cscw", "cscw-*.json"),
    'cscwDir': path.join(ioRoot, "cscw")
}

#%%
def corpusFilesToDaskBag(pathWithFilesGlob):
    return bag.read_text(str(pathWithFilesGlob),
                         encoding='utf-8', linedelimiter='\n')\
                         .str.strip().map(json.loads)

def combineArticleText(article):
    title = article["title"]
    venue = article["venue"]
    abstract = article["paperAbstract"]
    return  f"\nxbos xvenue {venue} xtitle {title} xabstract {abstract}"

def combineFixTokenize(article): # each line is an article as json
    aString = combineArticleText(article)
    fixedString = wt103RegexFixes(aString)
    return Tokenizer().proc_text(aString) # token arrays

bag2 = corpusFilesToDaskBag(ioPaths['cscwGlob']).map(combineFixTokenize)
processedText =  np.array(bag2.compute())
np.save(ioPaths['cscwDir'] + '\\arrayOfTokenLists.npy', processedText)
# processedText = np.load(ioPaths['cscwDir'] + '\\arrayOfTokenLists.npy')

#%%
import dill as pickle #to save default dict
maxVocabLength = 60000
vocabCounts = bag2.flatten().frequencies().topk(maxVocabLength, lambda x: x[1]).compute() #tuple of tuples
pd.DataFrame.from_records(vocabCounts).to_csv(ioPaths['cscwDir'] + '\\vocabCounts.csv',
                                        header=False, index=False) #watch for "
minVocabCount = 2
ixToVocab = [v[0] for v in vocabCounts if v[1] > minVocabCount]
ixToVocab.insert(0, '_pad_')
ixToVocab.insert(0, '_unk_')
vocabToIx = collections.defaultdict(lambda:0, {v:k for k, v in enumerate(ixToVocab)})

pickle.dump(ixToVocab, open(ioPaths['cscwDir'] + '\\ixToVocab.pkl', 'wb'))
pickle.dump(vocabToIx, open(ioPaths['cscwDir'] + '\\vocabToIx.pkl', 'wb'))

tokensAsIxs   = np.array([[vocabToIx[o] for o in p] for p in processedText])
train_tokensAsIxs, validation_tokensAsIxs = \
    sklearn.model_selection.train_test_split(tokensAsIxs, test_size=0.1)
np.save(ioPaths['cscwDir'] + '\\train_tokensAsIxs.npy', train_tokensAsIxs)
np.save(ioPaths['cscwDir'] + '\\validation_tokensAsIxs.npy', validation_tokensAsIxs)

#%%
client.close()