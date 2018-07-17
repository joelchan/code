#%%
import torch
import numpy as np

dtype = torch.float
device = torch.device("cpu")

aVector = torch.tensor([1,1])

xBasis = [0, -1] #i.e. ihat / right. where it lands after trans
yBasis = [1,  0] #i.e. jhat / up. where it lands after trans
rot90right = torch.tensor([[xBasis[0], yBasis[0]],
                           [xBasis[1], yBasis[1]]])
rot90left = torch.tensor([[0,-1],
                           [1,0]])
combineTransforms = rot90right.mm(rot90left) #will be identity matrix.note mm or matmul will work
rotatePointBy90   = rot90right.mv(aVector) # 1,1 but rotated so 1,-1. note matmul or mv will work
print('should be identity:\n', combineTransforms, '\nshould be 1,-1:', rotatePointBy90)

np_rot90right = rot90right.data.numpy()
np_rot90left = rot90left.data.numpy()
np_aVector = aVector.data.numpy()

print('now with numpy: \n'
      'should be identity:\n', np_rot90right.dot(np_rot90left),
      '\nshould be 1,-1:', np_rot90right.dot(np_aVector))

# to convert from numpy to torch
a = np.ones(5)
b = torch.from_numpy(a)
#%% matrix multiply
mustMatch = 3 # e.g. x is the the transform
nRowsInAndMMOut = 3
nColsInAndMMOut = 1
x = torch.randn(nRowsInAndMMOut, mustMatch, device=device, dtype=dtype)
y = torch.randn(mustMatch, nColsInAndMMOut, device=device, dtype=dtype)

x.mm(y) # like randomly rotating a random 3d point

mustMatch = 4 # won't change the output dims
nRowsInAndMMOut = 3
nColsInAndMMOut = 2
x = torch.randn(nRowsInAndMMOut, mustMatch, device=device, dtype=dtype)
y = torch.randn(mustMatch, nColsInAndMMOut, device=device, dtype=dtype)

x.mm(y).shape # like randomly rotating a random 3d point

#%% multiple regression
from sklearn.datasets import make_regression
rng = np.random.RandomState(0)
X, y = make_regression(n_samples=20, n_features=2, random_state=0, noise=4.0,
                       bias=100.0)

x = torch.tensor(X, dtype=dtype, requires_grad=True)
weights = torch.nn.Linear(x.shape[1], 1)

y = torch.tensor(y, dtype=dtype)

learning_rate = 1e-6
for t in range(x.shape[0]):
    y_pred = weights(x) #was x.mm(weights) the no bias way
    loss = (y_pred - y[t]).pow(2).sum()
    print(t, loss.item())
    loss.backward()
    # with torch.no_grad():
    #     weights -= learning_rate * weights.grad
    #     weights.grad.zero_()


