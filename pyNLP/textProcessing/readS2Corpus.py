import gzip, os, sys, csv
from pathlib import Path
import json
import dask.bag as bag
from dask.diagnostics import ProgressBar
from dask.distributed import Client
# from ipyparallel import Client

ProgressBar().register()
import time
from operator import itemgetter

global __file__ #relative paths that work in ipython dev or some other relative docker path
__file__ = globals().get('x', 'E:\\code\\pyNLP\\textProcessing')
thisFilesPath = Path(os.path.dirname(os.path.realpath(__file__)))
fileDir = os.path.dirname(os.path.realpath(__file__))
corpusPath = 'E:\\code\\pyNLP\\textProcessing\\corpus-2018-05-03\\txt\\s2-corpus-00.txt'
corpusDirPath = 'E:\\code\\pyNLP\\textProcessing\\corpus-2018-05-03\\txt'
samplePath = Path('E:\\code\\pyNLP\\textProcessing\\sample-S2-records.gz')
outDir = 'E:\\code\\pyNLP\\textProcessing\\corpus-2018-05-03\\filtered'
# with gzip.open(corpusPath, 'r') as f:
#     corpusString = f.read().decode('utf-8')
# print(time.process_time())
# # papers = [json.loads(p) for p in corpusString.strip().split('\n')]
def corpusFilesToDaskBag(pathOrGlobWithFiles):
    return bag.read_text(str( pathOrGlobWithFiles ), encoding='utf-8', linedelimiter='\n')\
                .str.strip().map(json.loads)

def saveCsv(listOfTuples):
    with open(corpusDirPath + '/journal_counts.csv', 'w', newline='',encoding='utf-8') as o:
        csv_out = csv.writer(o)
        csv_out.writerow(['name', 'freq'])
        for row in listOfTuples:
            csv_out.writerow(row)
    print(listOfTuples)

# if __name__ == '__main__':
client = Client(processes=False, threads_per_worker=4, n_workers=1, memory_limit='3GB')
#%%time

from corpusFilters import filterByJournal

bag1 = corpusFilesToDaskBag(corpusPath);
bag2 = bag1.filter(filterByJournal)
bag2.to_textfiles(outDir, name_function=None, compression='infer',
             encoding='utf-8', compute=True, get=None, storage_options=None)
# print(len(filteredArticles))



#%%

# print(set([p['journalName'] for p in papers if 'IEEE' in p['journalName']]))
#%%


# papers = []
# for i,s in enumerate(corpusString.strip().split('\n')):
#     try: # deal with entries that error
#         papers.append(json.loads(s))
#     except:
#         print('error for: ', i)
#         continue
# # print(len(papers))

#%%