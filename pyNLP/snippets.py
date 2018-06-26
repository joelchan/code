# %% paths
import gzip, os, sys
from pathlib import Path
from operator import itemgetter  # for faster sorting

print('terminal dir:  ', os.getcwd())
print('path to console py:  ', sys.argv[0])
print('string of dir of file:  ', os.path.dirname(os.path.realpath('__file__')))

# check for file
if not ('__file__' in vars()):
    print('no __file__ 1')
if '__file__' not in globals():
    print('no __file__ 2')

# relative paths that work in ipython dev or via python -r or in some random docker path
global __file__
__file__ = globals().get('__file__', 'your_default_here')
print('path object containing this file:  ', os.path.dirname(
    os.path.realpath(__file__)))  # see Path() for other operations

# %% itemgetter is fast
sorted([(1, 2), (2, 3)], key=itemgetter(1), reverse=True)

# %% timing stuff
import time

startTime = time.clock()
print(time.clock() - startTime)

# %% extend path in a py file. useful for non-nested modules
sys.path.extend(
    ['server',
     'textProcessing'
     ])

##
# bot = doc.to_bag_of_terms(
#      ngrams=(1, 2, 3), named_entities=True, weighting='count', normalize='lemma',
#      as_strings=True, filter_stops=True, drop_determiners=True)
#
# terms = sorted(bot.items(), key=lambda x: x[1], reverse=True)[:15]
# # [print(n) for n in terms]
#
# #better than singlerank or textrank
# terms = textacy.keyterms.sgrank(doc, n_keyterms=30, window_width=50, ngrams=(1, 2, 3, 4))
# ner = textacy.keyterms.aggregate_term_variants(set([i[0] for i in terms]))
#
# # print(ner)
# [print(n) for n in ner]
