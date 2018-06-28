# %%
import csv, json
from os import path
import dask.bag as bag
from dask.distributed import Client
from operator import itemgetter
from filterSemScholSettings import venueNames, keepList, removeList
import os
from shutil import copyfile

starOrNum, outDir = '*', '20180627' #'*' to run all 39 files. '01' just the first

isIpython = False # can only do ipython debugging with 1 thread
client = Client(processes=False, threads_per_worker=1 if isIpython else 4,
                n_workers=1, memory_limit='4GB')

corpusRoot = 'E:\\code\\pyNLP\\textProcessing\\corpus-2018-05-03'
inGlob  = path.join(corpusRoot, "txt", f"s2-corpus-{str(starOrNum)}.txt")
outRoot = path.join(corpusRoot, f'{outDir}')
os.makedirs(outRoot, exist_ok=True)
outGlob = path.join(outRoot, f'filtered-*.json')


def keepRemove(keepList, removeList, searchString):
    # if this is not behaving, check commas in settings

    # skip stuff we don't want
    for strToMatch in removeList:
        if strToMatch.lower() in searchString.lower():
            return False

    # keep it if it's got something we do want
    for strToMatch in keepList:
        if strToMatch.lower() in searchString.lower():
            return True

    # otherwise skip it
    return False


def filterSemanticScholar(article):
    venue = article["venue"].lower()
    hasVenue = len(article["venue"]) > 0
    hasJournalName = len(article['journalName']) > 0
    hasAbstract = len(article['paperAbstract']) > 0

    if (not hasVenue and not hasJournalName):
        return False

    if not hasAbstract:
        return False

    if (not hasVenue and hasJournalName):
        venue = article['journalName'].lower()

    # bellow filters by what's in filterSemScholSettings
    ents = ' '.join([item.lower() for item in article['entities']])
    searchString = ents.lower() + ' ' + article['paperAbstract'].lower() + ' ' \
                   + article['title'].lower() + ' ' + venue
    willKeep = keepRemove(keepList, removeList, searchString)
    if willKeep and 'rabbit' in searchString: print(searchString )
    return willKeep


def corpusFilesToDaskBag(pathOrGlobWithFiles):
    return bag.read_text(str(pathOrGlobWithFiles), encoding='utf-8',
                         linedelimiter='\n') \
        .str.strip().map(json.loads)


def calcPropFrequences(bag, propName):
    freqs = bag.pluck(propName).frequencies()
    return sorted(freqs.compute(), key=itemgetter(1), reverse=True)


# %%
bag1 = corpusFilesToDaskBag(inGlob)
bag2 = bag1.filter(filterSemanticScholar)
# bag of dicts needs .map(json.dumps). bag of strings doesnt
bag2.map(json.dumps).to_textfiles(outGlob)
client.close()
