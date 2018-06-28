# Extract, transform, and load
import csv, json
from os import path
import dask.bag as bag  # sort of a parallel unordered pandas dataframe
from dask.distributed import Client
import dask
from os import listdir
from operator import itemgetter
import pandas as pd
from textUtils import wt103RegexFixes
from fastai.text import *

debugging = 0  # e.g. using ipython
client = Client(processes=False, threads_per_worker=1 if debugging else 4,
                n_workers=1, memory_limit='4GB')

articleProps = ["title", "venue", "entities", "year", "paperAbstract"]
corpusRoot = 'E:\\code\\pyNLP\\textProcessing\\corpus-2018-05-03'
ioDir = path.join(corpusRoot, "20180627")
starOrNum = 'test' if debugging else '*'  # '*' to run all 39 files. '01' just the first
inGlob = path.join(ioDir, f"filtered-{str(starOrNum)}.json")


# %%
def corpusFilesToDaskBag(pathWithFilesGlob):
    return bag.read_text(str(pathWithFilesGlob),
                         encoding='utf-8', linedelimiter='\n') \
        .str.strip().map(json.loads)


def combineArticleText(article):
    title = article["title"]
    venue = article["venue"]
    abstract = article["paperAbstract"]
    return f"\nxbos xvenue {venue} xtitle {title} xabstract {abstract}"


def combineFixTokenize(article):  # each line is an article as json
    print(article["title"])
    aString = combineArticleText(article)
    fixedString = wt103RegexFixes(aString)
    return Tokenizer().proc_text(fixedString)  # token arrays


bag2 = corpusFilesToDaskBag(inGlob).map(combineFixTokenize)
processedText = np.array(bag2.compute()) #change compute() to take(10) for testing
np.save(ioDir + '\\arrayOfTokenLists.npy', processedText)
# processedText = np.load(ioPaths['cscwDir'] + '\\arrayOfTokenLists.npy')

# %%
import dill as pickle  # to save default dict

maxVocabLength = 60000
vocabCounts = bag2.flatten().frequencies().topk(maxVocabLength, lambda x: x[
    1]).compute()  # tuple of tuples
pd.DataFrame.from_records(vocabCounts).to_csv(ioDir + '\\vocabCounts.csv', header=False, index=False)  # watch for "
minVocabCount = 2
ixToVocab = [v[0] for v in vocabCounts if v[1] > minVocabCount]
ixToVocab.insert(0, '_pad_')
ixToVocab.insert(0, '_unk_')
vocabToIx = collections.defaultdict(lambda: 0,
                                    {v: k for k, v in enumerate(ixToVocab)})

pickle.dump(ixToVocab, open(ioDir + '\\ixToVocab.pkl', 'wb'))
pickle.dump(vocabToIx, open(ioDir + '\\vocabToIx.pkl', 'wb'))

tokensAsIxs = np.array([[vocabToIx[o] for o in p] for p in processedText])
train_tokensAsIxs, validation_tokensAsIxs = \
    sklearn.model_selection.train_test_split(tokensAsIxs, test_size=0.1)
np.save(ioDir + '\\train_tokensAsIxs.npy', train_tokensAsIxs)
np.save(ioDir + '\\validation_tokensAsIxs.npy', validation_tokensAsIxs)

# %%
client.close()
