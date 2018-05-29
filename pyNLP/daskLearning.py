#%%
import gzip, os, sys
from pathlib import Path
import json
import dask.bag as bag
from dask.distributed import Client

from dask.distributed import Client, progress

#%%
import dask.array as da
x = da.random.random((10000, 10000), chunks=(1000, 1000))
y = x + x.T
z = y[::2, 5000:].mean(axis=1)
z

z.compute()