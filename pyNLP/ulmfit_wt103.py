# %%
from fastai.text import *
from torchtext import vocab, data
from pathlib import Path

rootPath = Path('E:\code\pyNLP')
wt103Path = rootPath / 'wt103'  # download files @ http://files.fast.ai/models/*wt*
wt103FilePath = wt103Path / 'fwd_wt103.h5'
wt103Weights = torch.load(wt103FilePath,
                          map_location=lambda storage, loc: storage)
intToString = pickle.load(
    open(wt103Path / 'itos_wt103.pkl', 'rb'))  # int to string
stringToInt = collections.defaultdict(lambda: 0,
                                      {v: k for k, v in enumerate(intToString)})
nVocab = len(intToString)


# %%
# cosine similarity - to check quality of our sentence encoder
def cos_sim(v1, v2):
    return F.cosine_similarity(T(v1).unsqueeze(0), T(v2).unsqueeze(0)).mean()


weightDecay = 1e-7
backpropThruTime = 70
batchSize = 250
optimizationFunc = partial(optim.Adam, betas=(0.8, 0.99))
dropoutVals = np.array([0.25, 0.1, 0.2, 0.02, 0.15]) * 0.7
embedSize, nHidden, nLayers, padIx = 400, 1150, 3, 1
trn_dl = LanguageModelLoader(np.array([]), batchSize, backpropThruTime)
val_dl = LanguageModelLoader(np.array([]), batchSize, backpropThruTime)
md = LanguageModelData(rootPath, 1, nVocab, trn_dl, val_dl, bs=batchSize,
                       bptt=backpropThruTime)
dropoutVals = np.array([0.25, 0.1, 0.2, 0.02, 0.15]) * 0.7
learner = md.get_model(optimizationFunc, embedSize, nHidden, nLayers,
                       dropouti=dropoutVals[0], dropout=dropoutVals[1],
                       wdrop=dropoutVals[2],
                       dropoute=dropoutVals[3], dropouth=dropoutVals[4])
learner.model.load_state_dict(wt103Weights)
# rnn = RNN_Encoder(vs, em_sz, nh, nl, stoi['_pad_'])
# rnn.load_state_dict(wgts)
# m = get_language_model(vs, em_sz, nh, nl, stoi['_pad_'])
# model = LanguageModel(to_gpu(m))
# rnn = RNN_Learner({'path':''}, model, opt_fn=opt_fn)
# rnn.load_state_dict(wgts)

#

# %%
for var_name in learner.model.state_dict():
    print(var_name)

# %%
m = learner.model

x1 = ['apple company', 'apple tree', 'oranges', 'where is your cell phone']
tok1 = Tokenizer().proc_all(x1, 'en')
X1 = [[stringToInt[o1] for o1 in o] for o in tok1]
checkX1 = [[intToString[o1] for o1 in o] for o in X1]
m.eval()  # Turn off dropout
m.reset()  # set hidden layers


# Create reusable func for inference
# Laid out for readability - will refactor later
def run_model(X):
    kk0 = m[0](V(T([X[
                        0]])))  # first sentence in X - sentence level encoding....10 words 400 dim vecs
    kk1 = m[0](V(T([X[
                        1]])))  # second sentence in X - sentence level encoding....10 words 400 dim vecs
    kk2 = m[0](V(T([X[
                        2]])))  # third sentence in X - sentence level encoding....10 words 400 dim vecs

    kk0 = to_np(kk0)
    kk1 = to_np(kk1)
    kk2 = to_np(kk2)

    kk0 = (kk0[0][2][0][
        -1])  # 1st sentence encoding 400 dims. -1 is the last element that's supposed to have the final encoded state
    kk1 = (kk1[0][2][0][-1])  # 2nd sentence encoding 400 dims
    kk2 = (kk2[0][2][0][-1])  # 3rd sentence encoding 400 dims

    return kk0, kk1, kk2


kk0, kk1, kk2 = run_model(X1)
cos_sim(kk0, kk0), cos_sim(kk0, kk1), cos_sim(kk0, kk2)
# np.inner(kk0, kk0), np.inner(kk0, kk1), np.inner(kk0, kk2)

# %%
import warnings
warnings.filterwarnings('ignore')
tokenizer = lambda aString: Tokenizer().proc_text(aString)
str2numsArr = lambda aString: [stringToInt[o] for o in tokenizer(aString)]

def sample_model(m, s, l=40):
    wordsAsInts = str2numsArr(s);
    wordsAsTensors = T(wordsAsInts)
    t = VV(wordsAsTensors).unsqueeze(1)
    m[0].bs = 1
    m.eval()
    m.reset()
    res = m(t)

    allWords = ''
    for i in range(l):
        nextWordIx = res[0][-1].topk(2)[1]
        topN = [intToString[x.data[0]] for x in res[0][-1].topk(10)[1]]
        nextWordIx = nextWordIx[1] if nextWordIx.data[0] == 0 else nextWordIx[0]
        nextWord = intToString[nextWordIx.data[0]]
        allWords = allWords + ' ' + nextWord
        if nextWord == '.': break;
        wordsAsTensors = torch.cat((wordsAsTensors, T([nextWordIx])))
        res = m(VV(wordsAsTensors).unsqueeze(1))
    # m[0].bs=bs
    print(allWords)
sample_model(m, 'neuroscience is important because ')
