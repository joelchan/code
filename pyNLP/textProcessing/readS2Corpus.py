import gzip, os, sys, csv
from pathlib import Path
import json
import dask.bag as bag
from dask.diagnostics import ProgressBar
from dask.distributed import Client
ProgressBar().register()
import time
from operator import itemgetter

global __file__ #relative paths that work in ipython dev or some other relative docker path
__file__ = globals().get('x', 'E:\\code\\pyNLP\\textProcessing')
thisFilesPath = Path(os.path.dirname(os.path.realpath(__file__)))
fileDir = os.path.dirname(os.path.realpath(__file__))
corpusPath = 'E:\\code\\pyNLP\\textProcessing\\corpus-2018-05-03\\txt\\s2-corpus-*.txt'
corpusDirPath = 'E:\\code\\pyNLP\\textProcessing\\corpus-2018-05-03\\txt'
samplePath = Path('E:\\code\\pyNLP\\textProcessing\\sample-S2-records.gz')
# with gzip.open(corpusPath, 'r') as f:
#     corpusString = f.read().decode('utf-8')
# print(time.process_time())
# # papers = [json.loads(p) for p in corpusString.strip().split('\n')]
def loadCorpus():
    b = bag.read_text(str( corpusPath ), encoding='utf-8', linedelimiter='\n').str.strip().map(json.loads)
    x = b.pluck('journalName').frequencies()
    out = sorted(x.compute(), key=itemgetter(1), reverse=True)
    with open(corpusDirPath + '/journal_counts.csv', 'w', newline='',encoding='utf-8') as o:
        csv_out = csv.writer(o)
        csv_out.writerow(['name', 'freq'])
        for row in out:
            csv_out.writerow(row)
    print(out)


if __name__ == '__main__':
    client = Client(processes=False, threads_per_worker=4, n_workers=1, memory_limit='3GB')
    start = time.process_time()
    loadCorpus()
    print(time.process_time())

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