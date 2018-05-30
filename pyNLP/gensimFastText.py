#%%
import csv, json, time
from os import path
import dask.bag as bag # a bag is an unsorted list that we can work with in parallel
from dask.distributed import Client #e.g. Client(processes=False, threads_per_worker=4, n_workers=1, memory_limit='3GB')
from operator import itemgetter #for faster sorting
from gensim.models import FastText
import gensim
from operator import itemgetter #for faster sorting
from tabulate import tabulate
assert gensim.models.fasttext.FAST_VERSION > -1
ioRoot = 'E:\\code\\pyNLP\\textProcessing\\corpus-2018-05-03'
ioPaths = {
    'corpusAll':    path.join(ioRoot, "txt", "s2-corpus-*.txt"),
    'corpusFirst':  path.join(ioRoot, "txt", "s2-corpus-00.txt"),
    'sample':       path.join(ioRoot, "sample-S2-records.gz"),
    'filtered':     path.join(ioRoot, "filtered"),
    'filteredJSON': path.join(ioRoot, "filtered", "venueFiltered-*.json"),
}

client = Client(processes=False, threads_per_worker=4, n_workers=1, memory_limit='4GB')
def corpusFilesToDaskBag(pathOrGlobWithFiles):
    return bag.read_text(str( pathOrGlobWithFiles ), encoding='utf-8', linedelimiter='\n')\
                .str.strip().map(json.loads)

bag1 = corpusFilesToDaskBag(ioPaths['filteredJSON'])
titles = bag1.pluck('title').compute()
titles = list([t.split(' ') for t in titles])
client.close()
#%% Base model
startTime = time.clock()
model = None
model = FastText(titles[:100000], min_count=1, workers=4)
print(time.clock() - startTime)
model.most_similar(positive=['cognitive'])

#%% experiments
startTime = time.clock()
model2 = None
model2 = FastText(titles[:100000], min_count=1, workers=4, sg=1)
print(time.clock() - startTime)
r1 = model.most_similar(positive=['cognitive'])
r2 = model2.most_similar(positive=['cognitive'])
print(tabulate([[r1[i][0], r2[i][0]] for i, x in enumerate(r1)]))
# sg=1
# todo: gensim.models.phrases

#%%
