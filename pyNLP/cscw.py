# %%
from fastai.text import *
import html

embeddingSize, nHidden, nLayers = 400, 1150, 3

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

# learner.metrics = [accuracy] # for printing
# learner.freeze_to(-1) # only update last layer to tune new tokens
#
# lr=1e-3
# lrs = lr
# torch.backends.cudnn.enabled = False # deal with cudnn X pytorch .4 bug. Might work with pytorch update.
# learner.fit(lrs/2, 1, wds=wd, use_clr=(32,2), cycle_len=1)
# learner.save('lm_last_ft')
# learner.load('lm_last_ft')
#
# #%% now train the whole network
# learner.unfreeze()
# # learner.lr_find(start_lr=lrs/10, end_lr=lrs*10, linear=True)
# # learner.sched.plot()
# learner.fit(lrs, 1, wds=wd, use_clr=(20,10), cycle_len=15)
#
# learner.save('fineTunedCSCW')
# learner.save_encoder('fineTunedCSCW_enc')
# learner.sched.plot_loss()


phrases = [
    "human computer interaction",
    "HCI",
    'cognitive', 'sensemaking', 'comprehension', 'lip reading', 'reading',
    'articles', 'perception', 'notetaking', 'annotation', 'foraging',
    'formalization', 'ontology', 'NLP', 'machine learning', 'neural',
    'brain', 'intelligence', 'interaction', 'design', 'nonverbal',
    'sign language',
    'natural language processing', 'creativity', 'group creativity',
    'group dynamics', 'social',
    'reading comprehension', 'editing', 'code editor', 'vision',
    'graphic design', 'user research', 'UX',
    'word embeddings', 'words', 'crowdsourcing', 'database',
    'collaborative sensemaking', 'affinity diagram',
    'concept map', 'knowledge map', 'human research', 'tags', 'active reading',
    'user centered design'
]
# %%
learner.load('fineTunedCSCW')
learner.load_encoder('fineTunedCSCW_enc')
m = learner.model

def cos_sim(v1, v2):
    return F.cosine_similarity(T(v1).unsqueeze(0), T(v2).unsqueeze(0)).mean()

#%%
def prepareStringsForModel(aStringArr, vocabToIx):
    tokensLists = Tokenizer().proc_all(aStringArr, 'en')
    tokensAsIxs =  [[vocabToIx[tok] for tok in tokens] for tokens in tokensLists]
    tokFlat = np.array([item for sublist in tokensLists for item in sublist])
    ixFlat = np.array([item for sublist in tokensAsIxs for item in sublist])
    unknownWords = tokFlat[ixFlat == 0]
    return tokensAsIxs, unknownWords

tokensAsIxs, unknownWords = prepareStringsForModel(phrases, vocabToIx)

# %%
def runModelGetLastEncoderLayer(model, tokensAsIxs):
    model.eval()  # turns off dropout and autograd
    model.reset()  # models are stateful
    rnnEncoder = model[0]  # model[1] has decoder
    activationsWithoutDropOut, _ = rnnEncoder(
        V(T(tokensAsIxs).unsqueeze(0)))  # calls forward method
    lastLayer = to_np(activationsWithoutDropOut[2].data[0, -1, :])
    return lastLayer

getVec = lambda aString: runModelGetLastEncoderLayer(m, tokensAsIxs)
getVecs = lambda arryOfSentences: [getVec(sent) for sent in arryOfSentences]


# getVec('cognitive')
features = getVecs(phrases)

from sklearn.manifold import TSNE

def plot_similarity(labels, features):
    X_embedded = TSNE(n_components=2, perplexity=6).fit_transform(
        features)  # perplexity=4 seems good
    import matplotlib.pyplot as plt
    (fig, ax) = plt.subplots(figsize=(25, 16))
    ax.scatter(X_embedded[:, 0], X_embedded[:, 1], c="b")
    for i, txt in enumerate(labels):
        ax.annotate(txt, (X_embedded[i, 0] + .75, X_embedded[i, 1]))

plot_similarity(phrases, features)

# cos_sim(kk0, kk0), cos_sim(kk0, kk1), cos_sim(kk0, kk2)
# np.inner(kk0, kk0), np.inner(kk0, kk1), np.inner(kk0, kk2)

# %%
import warnings

warnings.filterwarnings('ignore')
tokenizer = lambda aString: Tokenizer().proc_text(aString)
str2numsArr = lambda aString: [vocabToIx[o] for o in tokenizer(aString)]


def sample_model(aModel, aString, nWordsGenerated=40):
    wordsAsInts = str2numsArr(aString)
    wordsAsTensors = T(wordsAsInts)
    t = VV(wordsAsTensors).unsqueeze(1)
    aModel[0].bs = 1
    aModel.eval()
    aModel.reset()
    res = aModel(t)

    allWords = ''
    for i in range(nWordsGenerated):
        nextWordIx = res[0][-1].topk(2)[1]
        topN = [ixToVocab[x.data[0]] for x in res[0][-1].topk(10)[1]]
        nextWordIx = nextWordIx[1] if nextWordIx.data[0] == 0 else nextWordIx[0]
        nextWord = ixToVocab[nextWordIx.data[0]]
        allWords = allWords + ' ' + nextWord
        if nextWord == '.': break;
        wordsAsTensors = torch.cat((wordsAsTensors, T([nextWordIx])))
        res = aModel(VV(wordsAsTensors).unsqueeze(1))
    print(allWords)


sample_model(m, 'in this paper ')
