import csv, json
from os import path
import dask.bag as bag
from dask.distributed import Client
from operator import itemgetter
from corpusFilters import filterByVenue

ioRoot = 'E:\\code\\pyNLP\\textProcessing\\corpus-2018-05-03'
#todo: change to a dataclass or named tuple and add to seperate file
ioPaths = {
    'corpusAll':    path.join(ioRoot, "txt", "s2-corpus-*.txt"),
    'corpusFirst':  path.join(ioRoot, "txt", "s2-corpus-00.txt"),
    'sample':       path.join(ioRoot, "sample-S2-records.gz"),
    'filtered':     path.join(ioRoot, "filtered")
}

def corpusFilesToDaskBag(pathOrGlobWithFiles):
    return bag.read_text(str( pathOrGlobWithFiles ), encoding='utf-8', linedelimiter='\n')\
                .str.strip().map(json.loads)

def saveCsv(listOfTuples, outFileName): #todo: pandas?
    with open(ioPaths.save + '\\' + outFileName, 'w', newline='',encoding='utf-8') as o:
        csv_out = csv.writer(o)
        csv_out.writerow(['name', 'freq'])
        for row in listOfTuples:
            csv_out.writerow(row)

# if __name__ == '__main__':
client = Client(processes=False, threads_per_worker=4, n_workers=1, memory_limit='3GB')

def calcFrequences(bag, propName):
    freqs = bag.pluck(propName).frequencies()
    return sorted(freqs.compute(), key=itemgetter(1), reverse=True)

bag1 = corpusFilesToDaskBag(ioPaths.corpusAll)
bag2 = bag1.filter(filterByVenue)

# bag of dicts needs .map(json.dumps). bag of strings doesnt
bag2.map(json.dumps).to_textfiles(path.join(ioPaths.filtered, 'venueFiltered-*.json'))
#todo: rename venueFiltered here and in the folder/files just filtered-timestamp-*.json
#todo: rename readS2Corpus to extractFromSemanticScholarCorpusFiles

