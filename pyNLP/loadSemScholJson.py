import csv, json
from os import path
import dask.bag as bag
from dask.distributed import Client
from operator import itemgetter

ioRoot = 'E:\\code\\pyNLP\\textProcessing\\corpus-2018-05-03'
ioPaths = {
    'corpusAll':    path.join(ioRoot, "txt", "s2-corpus-*.txt"),
    'corpusFirst':  path.join(ioRoot, "txt", "s2-corpus-00.txt"),
    'sample':       path.join(ioRoot, "sample-S2-records.gz"),
    'filtered':     path.join(ioRoot, "filtered"),
    'filteredJSON': path.join(ioRoot, "filtered", "venueFiltered-00.json"),
    'ulmfit':       path.join(ioRoot, "ulmfit")

}

def corpusFilesToDaskBag(pathOrGlobWithFiles):
    return bag.read_text(str(pathOrGlobWithFiles), encoding='utf-8',
                         linedelimiter='\n') \
        .str.strip().map(json.loads)

client = Client(processes=False, threads_per_worker=4, n_workers=1, memory_limit='4GB')
def corpusFilesToDaskBag(pathOrGlobWithFiles):
    return bag.read_text(str( pathOrGlobWithFiles ), encoding='utf-8', linedelimiter='\n')\
                .str.strip().map(json.loads)

bag1 = corpusFilesToDaskBag(ioPaths['filteredJSON'])

def calcWordFrequences(bag):
    freqs = bag.pluck('paperAbstract').str.lower().str.split()\
        .flatten().frequencies().topk(60000, lambda x: x[1])
    return freqs
#%%
import pandas as pd

bag2 = corpusFilesToDaskBag(ioPaths['corpusFirst'])
freqs = calcWordFrequences(bag2).compute()
pd.DataFrame.from_records(freqs).to_csv(ioPaths['ulmfit'] + '\\vocab.csv')
client.close()


#todo: consolidate 3 files with corpusFilesToDaskBag