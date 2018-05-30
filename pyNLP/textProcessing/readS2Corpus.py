import csv, json
import os.path.join as join
import dask.bag as bag # a bag is an unsorted list that we can work with in parallel
from dask.distributed import Client #e.g. Client(processes=False, threads_per_worker=4, n_workers=1, memory_limit='3GB')
from operator import itemgetter #for faster sorting

ioRoot = 'E:\\code\\pyNLP\\textProcessing\\corpus-2018-05-03'
ioPaths = {
    'corpusAll':    join(ioRoot, "txt", "s2-corpus-*.txt"),
    'corpusFirst':  join(ioRoot, "txt", "s2-corpus-00.txt"),
    'sample':       join(ioRoot, "sample-S2-records.gz"),
    'filtered':     join(ioRoot, "filtered")
}

def corpusFilesToDaskBag(pathOrGlobWithFiles):
    return bag.read_text(str( pathOrGlobWithFiles ), encoding='utf-8', linedelimiter='\n')\
                .str.strip().map(json.loads)

def saveCsv(listOfTuples, outFileName):
    with open(ioPaths.save + '\\' + outFileName, 'w', newline='',encoding='utf-8') as o:
        csv_out = csv.writer(o)
        csv_out.writerow(['name', 'freq'])
        for row in listOfTuples:
            csv_out.writerow(row)
    print(listOfTuples)

# if __name__ == '__main__':
client = Client(processes=False, threads_per_worker=4, n_workers=1, memory_limit='3GB')

def calcFrequences(bag, propName):
    freqs = bag.pluck(propName).frequencies()
    return sorted(freqs.compute(), key=itemgetter(1), reverse=True)

from corpusFilters import filterByVenue

bag1 = corpusFilesToDaskBag(ioPaths.corpusAll)
bag2 = bag1.filter(filterByVenue)
# bag of dicts needs .map(json.dumps). bag of strings doesnt
bag2.map(json.dumps).to_textfiles(join(ioPaths.filtered, 'venueFiltered-*.json'))



