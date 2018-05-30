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
model = FastText(titles[:100000], min_count=1, workers=4, sg=0)
print(time.clock() - startTime)
model.most_similar(positive=['cognitive'])

#%% experiments
startTime = time.clock()
model2 = None
model2 = FastText(titles[:100000], min_count=1, workers=4, sg=1)
print(time.clock() - startTime)
r1 = model.most_similar(positive=['cognitive'])
r2 = model2.most_similar(positive=['cognitive'])
print(tabulate([[r2[i][0], r1[i][0]] for i, x in enumerate(r1)],
               headers=['Model2', 'Model1'],
               tablefmt='orgtbl'))

#%% TSNE
words = ['cognitive', 'sensemaking', 'comprehension', 'reading',
         'articles', 'perception', 'notetaking', 'annotation', 'foraging',
         'formalization', 'ontology', 'NLP', 'machine learning', 'neural',
         'brain', 'intelligence', 'HCI', 'interaction', 'design']

neighbors = [model2.most_similar(positive=[w],topn=1)[0][0] for w in words]

vecs = [model2.wv[w] for w in words]

import numpy as np
from sklearn.manifold import TSNE
X_embedded = TSNE(n_components=2, perplexity=4).fit_transform(vecs)
X_embedded.shape
import matplotlib.pyplot as plt
(fig, ax) = plt.subplots(figsize=(15, 8))
ax.scatter(X_embedded[:,0], X_embedded[:,1], c="b")
for i, txt in enumerate(words):
    ax.annotate(txt + "\n" + neighbors[i], (X_embedded[i,0]+.75, X_embedded[i,1]))
# ax.scatter(X[green, 0], X[green, 1], c="g")
# sg=1, predict the word from the context, might need less data than CBOW/sg=0

# todo: gensim.models.phrases
# todo: remove punc

#%%
