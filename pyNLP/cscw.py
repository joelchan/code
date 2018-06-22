#%%
from fastai.text import *
import html

#%%
from fastai.text import *
import html

embeddingSize, nh, nl = 400, 1150, 3

rootPath = Path('E:\code\pyNLP')
wt103Path = rootPath / 'wt103'  # download files @ http://files.fast.ai/models/*wt*
wt103FilePath = wt103Path / 'fwd_wt103.h5'
wt103Weights = torch.load(wt103FilePath,
                          map_location=lambda storage, loc: storage)
ioRoot = 'E:\\code\\pyNLP\\textProcessing\\corpus-2018-05-03\\cscw'


ixToVocab = pickle.load(
    open(ioRoot + '\\ixToVocab.pkl', 'rb'))  # int to string
vocabToIx = collections.defaultdict(lambda: 0,
                                    {v: k for k, v in enumerate(ixToVocab)})
nVocab = len(ixToVocab)

encoderWeights = to_np(wt103Weights['0.encoder.weight'])
rowMean = encoderWeights.mean(0)

#%% Vocab matching
# create a new vocab, new words get wiki mean, known words get wiki weights
newWeights = np.zeros((nVocab, embeddingSize), dtype=np.float32)
for i,word in enumerate(ixToVocab):
    r = vocabToIx[word]
    newWeights[i] = encoderWeights[r] if r >= 0 else rowMean

wt103Weights['0.encoder.weight'] = T(newWeights)
wt103Weights['0.encoder_with_dropout.embed.weight'] = T(np.copy(newWeights))
wt103Weights['1.decoder.weight'] = T(np.copy(newWeights))

#%% update language model
wd=1e-7
bptt=40
bs=52
opt_fn = partial(optim.Adam, betas=(0.8, 0.99))
trainingData = np.load(ioRoot + '\\train_tokensAsIxs.npy')
validationData = np.load(ioRoot + '\\validation_tokensAsIxs.npy')

trn_dl = LanguageModelLoader(np.concatenate(trainingData), bs, bptt)
val_dl = LanguageModelLoader(np.concatenate(validationData), bs, bptt)
md = LanguageModelData(ioRoot, 1, nVocab, trn_dl, val_dl, bs=bs, bptt=bptt)

dropFactor = 0.5 # change this if under/over fitting. reduce for small datasets
drops = np.array([0.25, 0.1, 0.2, 0.02, 0.15])*dropFactor

learner= md.get_model(opt_fn, embeddingSize, nh, nl,
    dropouti=drops[0], dropout=drops[1], wdrop=drops[2], dropoute=drops[3],
    dropouth=drops[4])

learner.metrics = [accuracy] # for printing
learner.freeze_to(-1) # only update last layer to tune new tokens

lr=1e-3
lrs = lr
torch.backends.cudnn.enabled = False # deal with cudnn X pytorch .4 bug. Might work with pytorch update.
learner.fit(lrs/2, 1, wds=wd, use_clr=(32,2), cycle_len=1)
learner.save('lm_last_ft')
learner.load('lm_last_ft')

#%% now train the whole network
learner.unfreeze()
# learner.lr_find(start_lr=lrs/10, end_lr=lrs*10, linear=True)
# learner.sched.plot()
learner.fit(lrs, 1, wds=wd, use_clr=(20,10), cycle_len=15)

learner.save('fineTunedCSCW')
learner.save_encoder('fineTunedCSCW_enc')
learner.sched.plot_loss()

#%%
# %%
m = learner.model
def cos_sim(v1, v2):
    return F.cosine_similarity(T(v1).unsqueeze(0), T(v2).unsqueeze(0)).mean()

x1 = ['human computer interaction', 'HCI', 'cognitive science', 'neuroscience']
tok1 = Tokenizer().proc_all(x1, 'en')
print(tok1)
X1 = [[vocabToIx[o1] for o1 in o] for o in tok1]
checkX1 = [[ixToVocab[o1] for o1 in o] for o in X1]
m.eval()  # Turn off dropout
m.reset()  # set hidden layers


# Create reusable func for inference
# Laid out for readability - will refactor later
def run_model(X):
    kk0 = m[0](V(T([X[0]])))
    kk1 = m[0](V(T([X[1]])))
    kk2 = m[0](V(T([X[2]])))

    kk0 = to_np(kk0)
    kk1 = to_np(kk1)
    kk2 = to_np(kk2)

    kk0 = (kk0[0][2][0][-1])
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
str2numsArr = lambda aString: [vocabToIx[o] for o in tokenizer(aString)]

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
        topN = [ixToVocab[x.data[0]] for x in res[0][-1].topk(10)[1]]
        nextWordIx = nextWordIx[1] if nextWordIx.data[0] == 0 else nextWordIx[0]
        nextWord = ixToVocab[nextWordIx.data[0]]
        allWords = allWords + ' ' + nextWord
        if nextWord == '.': break;
        wordsAsTensors = torch.cat((wordsAsTensors, T([nextWordIx])))
        res = m(VV(wordsAsTensors).unsqueeze(1))
    # m[0].bs=bs
    print(allWords)


sample_model(m, 'in this paper ')