# %%
from fastai.text import *
from textUtils import wt103RegexFixes
import html
torch.backends.cudnn.enabled = False # deal with cudnn X pytorch .4 bug. Might work with pytorch update.

ioRoot = 'E:\\code\\pyNLP\\textProcessing\\corpus-2018-05-03\\cscw'
ixToVocab = pickle.load(
    open(ioRoot + '\\ixToVocab.pkl', 'rb'))  # int to string
vocabToIx = collections.defaultdict(lambda: 0,
                                    {v: k for k, v in enumerate(ixToVocab)})
nVocab = len(ixToVocab)
embeddingSize, nHidden, nLayers = 400, 1150, 3
m = get_language_model(nVocab, embeddingSize, nHidden, nLayers, int(vocabToIx['_pad_']))
load_model(m, ioRoot + '\\models\\fineTunedCSCW.h5')
load_model(m[0], ioRoot + '\\models\\fineTunedCSCW_enc.h5') #load encoder
m.cuda()
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

#%%
def prepareStringsForModel(aStringArr, vocabToIx):
    aStringArr = [wt103RegexFixes(x) for x in aStringArr]#todo sync with finetune
    tokensLists = Tokenizer().proc_all(aStringArr, 'en') #todo sync with finetune
    tokensAsIxs =  [[vocabToIx[tok] for tok in tokens] for tokens in tokensLists]
    tokFlat = np.array([item for sublist in tokensLists for item in sublist])
    ixFlat = np.array([item for sublist in tokensAsIxs for item in sublist])
    unknownWords = tokFlat[ixFlat == 0]
    return tokensAsIxs, unknownWords

tokensAsIxs, unknownWords = prepareStringsForModel(phrases, vocabToIx)
print('Unknown words: ', set(unknownWords))
# %%
def runModelGetLastEncoderLayer(model, tokensAsIxs):
    model.eval()  # turns off dropout and autograd
    model.reset()  # models are stateful
    rnnEncoder = model[0]  # model[1] has decoder
    activationsNoDropOut, _ = rnnEncoder(
        V(T(tokensAsIxs).unsqueeze(0)))  # calls forward method
    lastLayerIx = 2;
    lastLayer = to_np(activationsNoDropOut[lastLayerIx].data[0, -1, :]) #nullXnwordsX400
    return lastLayer

getVec = lambda tokensAsIxs: runModelGetLastEncoderLayer(m, tokensAsIxs)
getVecs = lambda arryOfTokensAsIxs: [getVec(sent) for sent in arryOfTokensAsIxs]

features = getVecs(tokensAsIxs)
import scipy.spatial.distance
dists = scipy.spatial.distance.cdist(features,features, 'cosine')

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
