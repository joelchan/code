#%% paths
import gzip, os, sys
from pathlib import Path
from operator import itemgetter #for faster sorting


print('terminal dir:  ', os.getcwd() )
print('path to console py:  ', sys.argv[0] )
print('string of dir of file:  ', os.path.dirname(os.path.realpath('__file__')) )

# check for file
if not ('__file__' in vars()):
    print('no __file__ 1')
if '__file__' not in globals():
    print('no __file__ 2')

# relative paths that work in ipython dev or via python -r or in some random docker path
global __file__
__file__ = globals().get('__file__', 'your_default_here')
print('path object containing this file:  ', os.path.dirname(os.path.realpath(__file__)) ) #see Path() for other operations
#%%
sorted([(1,2),(2,3)], key=itemgetter(1), reverse=True)
