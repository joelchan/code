# %%
from fastai.text import *
import html

embeddingSize, nHidden, nLayers = 400, 1150, 3

rootPath = Path('E:\code\pyNLP')
wt103Path = rootPath / 'wt103'  # download files @ http://files.fast.ai/models/*wt*
wt103FilePath = wt103Path / 'fwd_wt103.h5'
wt103Weights = torch.load(wt103FilePath,
                          map_location=lambda storage, loc: storage)
ioRoot = 'E:\\code\\pyNLP\\textProcessing\\corpus-2018-05-03\\20180627'

ixToVocab = pickle.load(
    open(ioRoot + '\\ixToVocab.pkl', 'rb'))  # int to string
vocabToIx = collections.defaultdict(lambda: 0,
                                    {v: k for k, v in enumerate(ixToVocab)})
nVocab = len(ixToVocab)
encoderWeights = to_np(wt103Weights['0.encoder.weight'])
rowMean = encoderWeights.mean(0)

# %% Vocab matching
# create a new vocab, new words get wiki mean, known words get wiki weights
newWeights = np.zeros((nVocab, embeddingSize), dtype=np.float32)
for i, word in enumerate(ixToVocab):
    r = vocabToIx[word]
    newWeights[i] = encoderWeights[r] if r >= 0 else rowMean

wt103Weights['0.encoder.weight'] = T(newWeights)
wt103Weights['0.encoder_with_dropout.embed.weight'] = T(np.copy(newWeights))
wt103Weights['1.decoder.weight'] = T(np.copy(newWeights))

# %% update language model
wd = 1e-7
bptt = 40
batchSize = 52
opt_fn = partial(optim.Adam, betas=(0.8, 0.99))
trainingData = np.load(ioRoot + '\\train_tokensAsIxs.npy')
validationData = np.load(ioRoot + '\\validation_tokensAsIxs.npy')

trn_dl = LanguageModelLoader(np.concatenate(trainingData), batchSize, bptt)
val_dl = LanguageModelLoader(np.concatenate(validationData), batchSize, bptt)
md = LanguageModelData(ioRoot, 1, nVocab, trn_dl, val_dl, bs=batchSize,
                       bptt=bptt)

dropFactor = 0.5  # change this if under/over fitting. reduce for small datasets
drops = np.array([0.25, 0.1, 0.2, 0.02, 0.15]) * dropFactor

learner = md.get_model(opt_fn, embeddingSize, nHidden, nLayers,
                       dropouti=drops[0], dropout=drops[1], wdrop=drops[2],
                       dropoute=drops[3],
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
# learner.lr_find(start_lr=lrs/10, end_lr=lrs*10, linear=True) # to find learning rate
# learner.sched.plot()
learner.fit(lrs, 1, wds=wd, use_clr=(20,10), cycle_len=15)

learner.save('fineTunedCSCW')
learner.save_encoder('fineTunedCSCW_enc')
learner.sched.plot_loss()