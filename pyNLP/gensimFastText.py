#%%
import csv, json, time
from os import path
import dask.bag as bag
from dask.distributed import Client
from gensim.models import FastText
import gensim
from tabulate import tabulate
import textacy.preprocess
assert gensim.models.fasttext.FAST_VERSION > -1
startTime = time.clock()
#todo: seperate file
stopWords = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves",
             "you", "your", "yours", "yourself", "yourselves", "he", "him",
             "his", "himself", "she", "her", "hers", "herself", "it", "its",
             "itself", "they", "them", "their", "theirs", "themselves",
             "what", "which", "who", "whom", "this", "that", "these",
             "those", "am", "is", "are", "was", "were", "be", "been",
             "being", "have", "has", "had", "having", "do", "does",
             "did", "doing", "a", "an", "the", "and", "but", "if",
             "or", "because", "as", "until", "while", "of", "at",
             "by", "for", "with", "about", "against", "between",
             "into", "through", "during", "before", "after", "above",
             "below", "to", "from", "up", "down", "in", "out", "on",
             "off", "over", "under", "again", "further", "then", "once",
             "here", "there", "when", "where", "why", "how", "all", "any",
             "both", "each", "few", "more", "most", "other", "some", "such",
             "no", "nor", "not", "only", "own", "same", "so", "than", "too",
             "very", "s", "t", "can", "will", "just", "don", "should", "now"]

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
def preProcessText(txt):
    cleanedUp = textacy.preprocess.preprocess_text(txt,
            lowercase=True, transliterate=True, no_punct=True, no_contractions=True )
    sentenceAsList = textacy.preprocess.normalize_whitespace(cleanedUp).split(' ')
    filteredSentence = [w for w in sentenceAsList if not w in stopWords]
    return filteredSentence
titles = bag1.pluck('title').map(preProcessText).compute()
# titles = list([t.split(' ') for t in titles])
client.close()
print(time.clock() - startTime)

#%% Base model
startTime = time.clock()
model = None
model = FastText(titles[:100000], min_count=1, workers=4, sg=0)
print(time.clock() - startTime)
model.most_similar(positive=['cognitive'])

#%% experiments
startTime = time.clock()
model2 = None
model2 = FastText(titles, min_count=10, workers=4, sg=1, window=10,size=100) #size=300 for transfer
# r1 = model.most_similar(positive=['cognitive'])
# r2 = model2.most_similar(positive=['cognitive'])
# print(tabulate([[r2[i][0], r1[i][0]] for i, x in enumerate(r1)],
#                headers=['Model2', 'Model1'],
#                tablefmt='orgtbl'))
print(time.clock() - startTime)

#%% TSNE
words = ['cognitive', 'sensemaking', 'comprehension', 'reading',
         'articles', 'perception', 'notetaking', 'annotation', 'foraging',
         'formalization', 'ontology', 'NLP', 'machine learning', 'neural',
         'brain', 'intelligence', 'HCI', 'interaction', 'design']
topN = lambda word, n: model2.most_similar(positive=[word],topn=n)
getNestedNth = lambda aList, nth: [x[nth] for x in aList]
neighbors = [[w] + getNestedNth(topN(w, 5),0) for w in words]
print(tabulate(neighbors))

vecs = [model2.wv[w] for w in words]

from sklearn.manifold import TSNE
X_embedded = TSNE(n_components=2, perplexity=4).fit_transform(vecs) # perplexity=4 seems good
X_embedded.shape
import matplotlib.pyplot as plt
(fig, ax) = plt.subplots(figsize=(15, 8))
ax.scatter(X_embedded[:,0], X_embedded[:,1], c="b")
for i, txt in enumerate(words):
    ax.annotate(txt, (X_embedded[i,0]+.75, X_embedded[i,1]))
# sg=1, predict the word from the context, might need less data than CBOW/sg=0

# todo: gensim.models.phrases
# todo: textacy.text_stats.TextStats
# todo: stopwords
# todo: table of sim rankd for domain
# todo: transfer learning with fasttext wiki corpus
# todo: spacy + abstracts
# todo: 80 char width

#%%

