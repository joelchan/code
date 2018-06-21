#%%
from fastai.text import *
import html

#%%
# imdb data http://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz
BOS = 'xbos'  # beginning-of-sentence tag
FLD = 'xfld'  # data field tag

PATH = Path('E:/fastai/data/aclImdb/')

CLAS_PATH = Path(PATH / 'imdb_clas/')
CLAS_PATH.mkdir(exist_ok=True)

LM_PATH = Path(PATH / 'imdb_lm/')
LM_PATH.mkdir(exist_ok=True)
tok_trn = np.load(LM_PATH/'tmp'/'tok_trn.npy')
CLASSES = ['neg', 'pos', 'unsup']


def get_texts(path):
    texts, labels = [], []
    for idx, label in enumerate(CLASSES):
        for i, fname in enumerate((path / label).glob('*.*')):
            texts.append(fname.open('r',encoding="utf8").read())
            labels.append(idx)
            if i > 100: break;
    return np.array(texts), np.array(labels)


trn_texts, trn_labels = get_texts(PATH / 'train')
val_texts, val_labels = get_texts(PATH / 'test')


col_names = ['labels', 'text']

np.random.seed(42)
trn_idx = np.random.permutation(len(trn_texts))
val_idx = np.random.permutation(len(val_texts))

trn_texts = trn_texts[trn_idx]
val_texts = val_texts[val_idx]

trn_labels = trn_labels[trn_idx]
val_labels = val_labels[val_idx]

df_trn = pd.DataFrame({'text': trn_texts, 'labels': trn_labels},
                      columns=col_names)
df_val = pd.DataFrame({'text': val_texts, 'labels': val_labels},
                      columns=col_names)

df_trn[df_trn['labels'] != 2].to_csv(CLAS_PATH / 'train.csv', header=False,
                                     index=False)
df_val.to_csv(CLAS_PATH / 'test.csv', header=False, index=False)

(CLAS_PATH / 'classes.txt').open('w').writelines(f'{o}\n' for o in CLASSES)
trn_texts,val_texts = sklearn.model_selection.train_test_split(
    np.concatenate([trn_texts,val_texts]), test_size=0.1)

df_trn = pd.DataFrame({'text':trn_texts, 'labels':[0]*len(trn_texts)}, columns=col_names)
df_val = pd.DataFrame({'text':val_texts, 'labels':[0]*len(val_texts)}, columns=col_names)


# csv format for each row is just: labelNumber, reviewText
df_trn.to_csv(LM_PATH/'train.csv', header=False, index=False)
df_val.to_csv(LM_PATH/'test.csv', header=False, index=False)

chunksize = 24000  # to save memory

re1 = re.compile(r'  +')

def fixup(x):
    x = x.replace('#39;', "'").replace('amp;', '&').replace('#146;', "'") \
        .replace('nbsp;', ' ').replace('#36;', '$').replace('\\n', "\n") \
        .replace('quot;',"'") \
        .replace('<br />', "\n").replace('\\"', '"').replace('<unk>', 'u_n')\
        .replace(' @.@ ', '.').replace(' @-@ ', '-').replace('\\', ' \\ ')
    return re1.sub(' ', html.unescape(x))


def get_texts(df, n_lbls=1):
    labels = df.iloc[:, range(n_lbls)].values.astype(np.int64)
    texts = f'\n{BOS} {FLD} 1 ' + df[n_lbls].astype(str)
    for i in range(n_lbls + 1,
                   len(df.columns)): texts += f' {FLD} {i-n_lbls} ' + \
                                              df[i].astype(str)
    texts = texts.apply(fixup).values.astype(str)
    print(texts.shape)
    tok = Tokenizer().proc_all_mp(partition_by_cores(texts))
    return tok, list(labels),texts


def get_all(df, n_lbls):
    tok, labels, texts = [], [], []
    for i, r in enumerate(df):
        print(i)
        tok_, labels_, texts_ = get_texts(r, n_lbls)
        tok += tok_
        labels += labels_
    return tok, labels, texts_


df_trn = pd.read_csv(LM_PATH / 'train.csv', header=None, chunksize=chunksize)
df_val = pd.read_csv(LM_PATH / 'test.csv', header=None, chunksize=chunksize)

tok_trn, trn_labels, trn_texts = get_all(df_trn, 1)
tok_val, val_labels, val_texts = get_all(df_val, 1)
#%%
(LM_PATH / 'tmp').mkdir(exist_ok=True)

np.save(LM_PATH/'tmp'/'trn_labels.npy', trn_labels)
np.save(LM_PATH/'tmp'/'val_labels.npy', val_labels)
np.save(LM_PATH/'tmp'/'tok_trn.npy', tok_trn) #arrays of tokens for training
np.save(LM_PATH/'tmp'/'tok_val.npy', tok_val) #arrays of tokens for validation

tok_trn = np.load(LM_PATH/'tmp'/'tok_trn.npy')
tok_val = np.load(LM_PATH/'tmp'/'tok_val.npy')

freq = Counter(p for o in tok_trn for p in o)
freq.most_common(25)

max_vocab = 60000
min_freq = 2

ixToVocabIMDB = [o for o, c in freq.most_common(max_vocab) if c > min_freq]
ixToVocabIMDB.insert(0, '_pad_')
ixToVocabIMDB.insert(0, '_unk_')

vocabToIxIMDB = collections.defaultdict(lambda:0, {v:k for k, v in enumerate(ixToVocabIMDB)})
len(ixToVocabIMDB)

trainingData = np.array([[vocabToIxIMDB[o] for o in p] for p in tok_trn])   # list of lists of tokens as ixs
validationData = np.array([[vocabToIxIMDB[o] for o in p] for p in tok_val]) # list of lists of tokens as ixs

np.save(LM_PATH /'tmp' /'trn_ids.npy', trainingData)
np.save(LM_PATH /'tmp' /'val_ids.npy', validationData)
pickle.dump(ixToVocabIMDB, open(LM_PATH / 'tmp' / 'itos.pkl', 'wb'))

trainingData = np.load(LM_PATH / 'tmp' / 'trn_ids.npy')
validationData = np.load(LM_PATH / 'tmp' / 'val_ids.npy')
ixToVocabIMDB = pickle.load(open(LM_PATH / 'tmp' / 'itos.pkl', 'rb')) #todo rename

nVocabIMDB=len(ixToVocabIMDB) #todo rename nVocab
nVocabIMDB, len(trainingData)

#%% wiki text convertion
embeddingSize, nh, nl = 400, 1150, 3

rootPath = Path('E:\code\pyNLP')
wt103Path = rootPath / 'wt103'  # download files @ http://files.fast.ai/models/*wt*
wt103FilePath = wt103Path / 'fwd_wt103.h5'
wt103Weights = torch.load(wt103FilePath,
                          map_location=lambda storage, loc: storage)
ixToVocab = pickle.load(
    open(wt103Path / 'itos_wt103.pkl', 'rb'))  # int to string
vocabToIx = collections.defaultdict(lambda: 0,
                                    {v: k for k, v in enumerate(ixToVocab)})
nVocab = len(ixToVocab)

encoderWeights = to_np(wt103Weights['0.encoder.weight'])
rowMean = encoderWeights.mean(0)


#%% Vocab matching
# create a new vocab, new words get wiki mean, known words get wiki weights
newWeights = np.zeros((nVocabIMDB, embeddingSize), dtype=np.float32)
for i,word in enumerate(ixToVocabIMDB):
    r = vocabToIx[word]
    newWeights[i] = encoderWeights[r] if r >= 0 else rowMean

wt103Weights['0.encoder.weight'] = T(newWeights)
wt103Weights['0.encoder_with_dropout.embed.weight'] = T(np.copy(newWeights))
wt103Weights['1.decoder.weight'] = T(np.copy(newWeights))

#%% update language model
wd=1e-7
bptt=70
bs=52
opt_fn = partial(optim.Adam, betas=(0.8, 0.99))

trn_dl = LanguageModelLoader(np.concatenate(trainingData), bs, bptt)
val_dl = LanguageModelLoader(np.concatenate(validationData), bs, bptt)
md = LanguageModelData(PATH, 1, nVocabIMDB, trn_dl, val_dl, bs=bs, bptt=bptt)

dropFactor = 0.7 # change this if under/over fitting. reduce for small datasets
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

learner.save('lm1')
learner.save_encoder('lm1_enc')
learner.sched.plot_loss()