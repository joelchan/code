# %%
from fastai.text import *
import html
from pathlib import Path
import scipy.spatial.distance
from sklearn.manifold import TSNE

torch.backends.cudnn.enabled = False  # deal with cudnn X pytorch .4 bug. Might work with pytorch update.


def loadModel(ixToVocabPath, modelWeightsPath, encPath, useCuda=0):
    ixToVocab = pickle.load(
        open(str(ixToVocabPath), 'rb'))  # int to string
    vocabToIx = collections.defaultdict(lambda: 0,
                                        {v: k for k, v in enumerate(ixToVocab)})
    nVocab = len(ixToVocab)
    embeddingSize, nActivations, nLayers = 400, 1150, 3  # for the wikitext model
    pytorchModel = get_language_model(nVocab, embeddingSize, nActivations,
                                      nLayers,
                                      int(vocabToIx['_pad_']))
    load_model(pytorchModel, str(modelWeightsPath))
    load_model(pytorchModel[0], str(encPath))  # load encoder
    if not useCuda:
        pytorchModel.cpu()
    return pytorchModel, ixToVocab, vocabToIx


def wt103RegexFixes(x):
    re1 = re.compile(r'  +')
    x = x.replace('#39;', "'").replace('amp;', '&').replace('#146;', "'") \
        .replace('nbsp;', ' ').replace('#36;', '$').replace('\\n', "\n") \
        .replace('quot;', "'") \
        .replace('<br />', "\n").replace('\\"', '"').replace('<unk>', 'u_n') \
        .replace(' @.@ ', '.').replace(' @-@ ', '-').replace('\\', ' \\ ')
    return re1.sub(' ', html.unescape(x))


def prepareStringsForModel(aStringArr, vocabToIx):
    aStringArr = [wt103RegexFixes(x) for x in
                  aStringArr]  # todo sync with finetune
    tokensLists = Tokenizer().proc_all(aStringArr,
                                       'en')  # todo sync with finetune
    tokensAsIxs = [[vocabToIx[tok] for tok in tokens] for tokens in tokensLists]
    tokFlat = np.array([item for sublist in tokensLists for item in sublist])
    ixFlat = np.array([item for sublist in tokensAsIxs for item in sublist])
    unknownWords = tokFlat[ixFlat == 0]
    return tokensAsIxs, unknownWords  # unknownWords == OOV


def runModelGetLastEncoderLayer(model, tokensAsIxs, useCuda):
    model.eval()  # turns off dropout and autograd
    model.reset()  # models are stateful
    rnnEncoder = model[0]  # model[1] has decoder
    activationsNoDropOut, _ = rnnEncoder(
        T(tokensAsIxs, cuda=useCuda).unsqueeze(0))  # calls forward method
    lastLayerIx = 2;
    lastLayer = to_np(
        activationsNoDropOut[lastLayerIx].data[0, -1, :])  # nullXnwordsX400
    return lastLayer


def getVectors(stringList, model, vocabToIx, useCuda):
    tokensAsIxs, unknownWords = prepareStringsForModel(stringList, vocabToIx)
    vectors = [runModelGetLastEncoderLayer(model, toks, useCuda)
               for toks in tokensAsIxs]
    return vectors


def textGeneration(aString, aModel, ixToVocab, vocabToIx, useCuda,
                   nWordsGenerated=40):
    import warnings
    warnings.filterwarnings('ignore')
    tokenizer = lambda aString: Tokenizer().proc_text(aString)
    str2numsArr = lambda aString: [vocabToIx[o] for o in tokenizer(aString)]
    wordsAsInts = str2numsArr(aString)
    wordsAsTensors = T(wordsAsInts, cuda=useCuda)
    t = T(wordsAsTensors, cuda=useCuda).unsqueeze(1)
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
        wordsAsTensors = torch.cat(
            (wordsAsTensors, T([nextWordIx], cuda=useCuda)))
        res = aModel(wordsAsTensors.unsqueeze(1))
    print(allWords)


class rnnProduction:
    """
    usage:
    # download model @ http://files.fast.ai/models/*wt*
    from testData import phrases # just a list of strings
    ioRoot = Path('E:\\code\\pyNLP\\wt103') #folder with files
    ixToVocabPath = ioRoot / 'itos_wt103.pkl'
    modelWeightsPath = ioRoot / 'fwd_wt103.h5'
    encPath = ioRoot / 'fwd_wt103_enc.h5'
    rnn = rnnProduction(ixToVocabPath, modelWeightsPath, encPath)
    vectors = rnn.getVectorsFromList(phrases)
    pairWiseDist = rnn.getPairWiseDistance(vectors)
    tsnePoints = rnn.getTSNE(vectors)
    genText = rnn.getNextWords('cognitive science is important because ')

    Note: CPU only now, but it has worked on GPU. Look into wrapping
    the pytorch tensors with pytorch variables if GPU is needed.
    """

    def __init__(self, ixToVocabPath, modelWeightsPath, encPath, useCuda=0):
        self.ixToVocabPath, self.modelWeightsPath, self.encPath, self.useCuda \
            = ixToVocabPath, modelWeightsPath, encPath, useCuda
        self.pytorchModel, self.ixToVocab, self.vocabToIx = \
            loadModel(ixToVocabPath, modelWeightsPath, encPath, useCuda=useCuda)

    def getVectorsFromList(self, stringList):
        return getVectors(stringList, self.pytorchModel, self.vocabToIx,
                          self.useCuda)

    def getPairWiseDistance(self, vectors):
        return scipy.spatial.distance.cdist(vectors, vectors, 'cosine')

    def getTSNE(self, vectors):  # todo umap is faster
        return TSNE(n_components=2, perplexity=6).fit_transform(vectors)

    def getNextWords(self, aString, nWordsGenerated=40):
        return textGeneration(aString, self.pytorchModel, self.ixToVocab,
                              self.vocabToIx, self.useCuda,
                              nWordsGenerated=nWordsGenerated)