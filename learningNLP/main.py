#%%
import spacy
nlp = spacy.load('en')
import os, sys
#%% spacy creates a doc object which is split into tokens
# space-case rules, then prefix "(<[, suffix, infix -
doc = nlp(u'pre-fix')
assert doc[1].text == '-' #infixes are seperated

doc = nlp(u"Apple's looking at buying (U.K.) startup for $1 billion")
assert doc[1].text == "'s" #contractions split off
assert doc[7].text == ")" #surrounding punc seperated
assert doc[6].text == 'U.K.' #acronymns kept together
assert doc[-2].text == '1' #numbers seperated from units
assert doc[-3].text == '$' #units seperated from numbers


# use token.attr_ to get human readable version
def showTokens(doc):
    for i, token in enumerate(doc):
        print(i, token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
              token.shape_, token.is_alpha, token.is_stop)

assert spacy.explain("VBZ") == "verb, 3rd person singular present"

def showEntities(doc):
    for ent in doc.ents:
        print(ent.text, ent.start_char, ent.end_char, ent.start, ent.end, ent.label_)

def entitiesInDocOrText(doc):
    ent = doc.ents[0]
    print(ent)
    tokenIndexed = doc[ent.start:ent.end]
    originalTextIndexed = doc.text[ent.start_char:ent.end_char]
    print(tokenIndexed, originalTextIndexed) # both Apple

#%% only core_lg and vectors_lg models have vectors, 'en' doesn't
tokens = nlp(u'dog cat banana')

def showSimilarityOfTokens(tokens):
    for token1 in tokens:
        for token2 in tokens:
            print(token1.similarity(token2))

#%% words are hashed to save space under the hood, but access is symmetrical
doc = nlp(u'I love coffee')
assert doc.vocab.strings[u'coffee'] == 3197928453018144401 #a 'lexeme'
assert doc.vocab.strings[3197928453018144401] == u'coffee'
len(doc.vocab) #1344233 lexemes for lg

def showLexemes(doc):
    for word in doc:
        lexeme = doc.vocab[word.text]
        print(lexeme.text, lexeme.orth, lexeme.shape_, lexeme.prefix_, lexeme.suffix_,
              lexeme.is_alpha, lexeme.is_digit, lexeme.is_title, lexeme.lang_)

#%% save/load to disk in an os save way
doc = nlp(u'I love coffee')
savedDocFile = os.path.join(os.getcwd(), 'testsave.bin');
doc.to_disk(savedDocFile) # save the processed Doc
from spacy.tokens import Doc # to create empty Doc
from spacy.vocab import Vocab # to create empty Vocab
doc = Doc(Vocab()).from_disk(savedDocFile) # load processed Doc

#%% noun chunks and sentences
doc = nlp(u"Peach emoji is where it has always been. Peach is the superior " +
          u"emoji. It's outranking eggplant ")

assert list(doc.noun_chunks)[0].text == u'Peach emoji' #note you need to listify the noun chunks
sentences = list(doc.sents)
assert len(sentences) == 3
assert sentences[1].text == u'Peach is the superior emoji.'

#%% part of speech
doc = nlp(u'Apple is looking at buying U.K. startup for $1 billion')
apple = doc[0]
assert [apple.tag_, apple.tag] == [u'NNP', 15794550382381185553]
assert [apple.shape_, apple.shape] == [u'Xxxxx', 16072095006890171862]
assert apple.is_alpha == True
assert apple.is_punct == False

billion = doc[10]
assert billion.is_digit == False
assert billion.like_num == True
assert billion.like_email == False

#%% more vocab/lexeme/hash adding vocab
doc = nlp(u'I love coffee')
beer_hash = doc.vocab.strings.add(u'beer') # 3073001599257881079
beer_text = doc.vocab.strings[beer_hash] # 'beer'

#%% Recognise and update named entities NER
from spacy.tokens import Span
doc = nlp(u'Netflix is hiring a new VP of global policy')
assert doc.ents[0].label_ == 'PERSON'; #netflix is incorrectly a person, VP should be a person but is org
doc.ents = [Span(doc, 0, 1, label=doc.vocab.strings[u'ORG']),
            Span(doc, 5, 6, label=doc.vocab.strings[u'PERSON'])] #ents is a tuple so have to rewrite the whole thing
showEntities(doc)

#%% train and update a nn model
import spacy
import random

nlp = spacy.load('en')
train_data = [("Uber blew through $1 million", {'entities': [(0, 4, 'ORG')]})]

with nlp.disable_pipes(*[pipe for pipe in nlp.pipe_names if pipe != 'ner']):
    optimizer = nlp.begin_training()
    for i in range(10):
        random.shuffle(train_data)
        for text, annotations in train_data:
            nlp.update([text], [annotations], sgd=optimizer)
savedPath = os.path.join(os.getcwd(), 'model');
nlp.to_disk(savedPath)

#%% dependency parsing with visualization
from spacy import displacy

doc_dep = nlp(u'This is a sentence.')
displacy.serve(doc_dep, style='dep')

doc_ent = nlp(u'When Sebastian Thrun started working on self-driving cars at Google '
              u'in 2007, few people outside of the company took him seriously.')
displacy.serve(doc_ent, style='ent')

#%% Match text with token rules
from spacy.matcher import Matcher
matcher = Matcher(nlp.vocab)
def set_sentiment(matcher, doc, i, matches):
    doc.sentiment += 0.1

pattern1 = [{'ORTH': 'Google'}, {'ORTH': 'I'}, {'ORTH': '/'}, {'ORTH': 'O'}]
matcher.add('GoogleIO', None, pattern1) # match "Google I/O" or "Google i/o"
matches = nlp('google i/o should be matched')
showTokens(matches)

#%% multithreading
texts = [u'One document.', u'...', u'Lots of documents']
# .pipe streams input, and produces streaming output
iter_texts = (texts[i % 3] for i in range(10))
for i, doc in enumerate(nlp.pipe(iter_texts, batch_size=50, n_threads=4)):
    assert doc.is_parsed
    if i == 100:
        break

#%% dependency walking
def dependency_labels_to_root(token):
    """Walk up the syntactic tree, collecting the arc labels."""
    dep_labels = []
    while token.head != token:
        dep_labels.append([token.dep_, token.text])
        token = token.head
    return dep_labels

doc = nlp('stuff is a test')

print(dependency_labels_to_root(doc[-1]))

#%% render html
def put_spans_around_tokens(doc, get_classes):
    """Given some function to compute class names, put each token in a
    span element, with the appropriate classes computed. All whitespace is
    preserved, outside of the spans. (Of course, HTML won't display more than
    one whitespace character it – but the point is, no information is lost
    and you can calculate what you need, e.g. <br />, <p> etc.)
    """
    output = []
    html = '<span class="{classes}">{word}</span>{space}'
    for token in doc:
        if token.is_space:
            output.append(token.text)
        else:
            classes = ' '.join(get_classes(token))
            output.append(html.format(classes=classes, word=token.text, space=token.whitespace_))
    string = ''.join(output)
    string = string.replace('\n', '')
    string = string.replace('\t', '    ')
    return string

def get_classess(token):
    print(token.pos_)
    return [token.pos_]

doc = nlp('here is a sentence we want to convert to html')
print(put_spans_around_tokens(doc, get_classess))

#%% guides - Noun chunks
doc = nlp(u'Autonomous cars shift insurance liability toward manufacturers')
for chunk in doc.noun_chunks:
    print(chunk.text, chunk.root.text, chunk.root.dep_,
          chunk.root.head.text)


#%%  navigating the parse tree: loop token and loop deps to find things
from spacy.symbols import nsubj, VERB
# Finding a verb with a subject from below — good
for possible_subject in doc:
    dep = possible_subject.dep
    head_pos = possible_subject.head.pos
    depText = possible_subject.text
    headText = possible_subject.head.text
    if dep == nsubj and  head_pos == VERB:
        print(depText, headText)

#%% syntax lefts and rights
doc = nlp(u'bright red apples on the tree')
assert [token.text for token in doc[2].lefts] == [u'bright', u'red']
assert [token.text for token in doc[2].rights] == ['on']
assert doc[2].n_lefts == 2
assert doc[2].n_rights == 1

#%% up and down the syntax tree with Token.subtree, Token.ancestors. check with .is_ancestor()
doc = nlp(u'Very autonomous cars shift insurance liability toward manufacturers')
print('sentence head: ', [token for token in doc if token.head == token])# there are many heads syntaxly, but spacy has one .head per sentence.
root = [token for token in doc if token.head == token][0]
subject = list(root.lefts)[0]
print(subject, root, '\n---')
# given some token list deps in sentence order, e.g. noun phrase root. sentence head will return entire sentence.
for descendant in doc[5].subtree: # doc5=liability
    print(descendant.text, descendant.dep_) # insurance liability

for ancestor in doc[4].ancestors: # given some token list deps in sentence order. sentence head will return entire sentence.
    print(ancestor.text, ancestor.dep_) #doc4=insurance, ancs = liability -> shift

#%% left_edge right_edge: useful to merge phrases into one token slot
doc = nlp(u'Credit and mortgage account holders must submit their requests')
print(doc[4].left_edge.i, doc[4].right_edge.i+1)
span = doc[doc[4].left_edge.i : doc[4].right_edge.i+1]
span.merge() #convert many tokens into one
for token in doc: #now doc[0] is 'Credit and mortgage account holders'
    print(token.text, token.pos_, token.dep_, token.head.text)

#%% NER named entity recognition 101
doc = nlp(u'San Francisco considers banning sidewalk delivery robots')

# document level
ents = [(e.text, e.start_char, e.end_char, e.label_) for e in doc.ents]
assert ents == [(u'San Francisco', 0, 13, u'GPE')]

# token level - entities not merged to single token
ent_san = [doc[0].text, doc[0].ent_iob_, doc[0].ent_type_] #iob is inside/outside/begining of entity
ent_francisco = [doc[1].text, doc[1].ent_iob_, doc[1].ent_type_]
assert ent_san == [u'San', u'B', u'GPE']
assert ent_francisco == [u'Francisco', u'I', u'GPE']

#%% set your own entities with spans set to ents
from spacy.tokens import Span

doc = nlp(u'Netflix is hiring a new VP of global policy')
# the model didn't recognise any entities :(

ORG = doc.vocab.strings[u'ORG'] # get hash value of entity label
netflix_ent = Span(doc, 0, 1, label=ORG) # create a Span for the new entity, token level index will set start/end char
doc.ents = [netflix_ent]

ents = [(e.text, e.start_char, e.end_char, e.label_) for e in doc.ents] #_char at the string level. .start for token level
assert ents == [(u'Netflix', 0, 7, u'ORG')]

#%% custom tokenization
from spacy.symbols import ORTH, LEMMA, POS, TAG

nlp = spacy.load('en')
doc = nlp(u'gimme that') # phrase to tokenize
assert [w.text for w in doc] == [u'gimme', u'that'] # current tokenization

# add special case rule
special_case = [{ORTH: u'gim', LEMMA: u'give', POS: u'VERB'}, {ORTH: u'me'}]
nlp.tokenizer.add_special_case(u'gimme', special_case)
assert [w.text for w in nlp(u'gimme that')] == [u'gim', u'me', u'that']
# Pronoun lemma is returned as -PRON-!
assert [w.lemma_ for w in nlp(u'gimme that')] == [u'give', u'-PRON-', u'that']

#%% rule-based matching
from spacy.matcher import Matcher

matcher = Matcher(nlp.vocab)
# add match ID "HelloWorld" with no callback and one pattern
pattern = [{'LOWER': 'hello'}, {'IS_PUNCT': True}, {'LOWER': 'world'}]
matcher.add('HelloWorld', None, pattern)

doc = nlp(u'Hello, world! Hello world!')
matches = matcher(doc)
for match_id, start, end in matches:
    string_id = nlp.vocab.strings[match_id]  # 'HelloWorld'
    span = doc[start:end]                    # the matched span
print(span)
# there are many attribute types such as pos, tag, dep, lemma so it goes beyond regexing

#%% custom pipeline components from function
def my_component(doc): #pipes take and return a doc. think linux cat file | grep 'something'
    print("After tokenization, this doc has %s tokens." % len(doc))
    if len(doc) < 10:
        print("This is a pretty short document.")
    return doc

nlp.add_pipe(my_component, name='print_info', first=True) #tokenizer is technically first, but isnt' a doc->doc pipe
print(nlp.pipe_names) # ['print_info', 'tagger', 'parser', 'ner']
doc = nlp(u"This is a sentence.")

#%% custom pipeline components from class: when you want to save some state in the pipe
class MyComponent(object):
    name = 'printstuff'

    def __init__(self, vocab, short_limit=10):
        self.vocab = vocab
        self.short_limit = short_limit

    def __call__(self, doc):
        if len(doc) < self.short_limit:
            print("This is a pretty short document.")
        return doc

my_component = MyComponent(nlp.vocab, short_limit=25)
nlp.add_pipe(my_component, first=True)
doc = nlp(u"This is a sentence.")

#%% attribute extension
Doc.set_extension('hello', default=True) # now you can do doc._.hello = False
def get_hello_value(): return True;
def set_hello_value(): return True;
#property extension
Doc.set_extension('hello', getter=get_hello_value, setter=set_hello_value)
assert doc._.hello
doc._.hello = 'Hi!'
#method extension
Doc.set_extension('hello', method=lambda doc, name: 'Hi {}!'.format(name)) #note how doc is first
assert doc._.hello('person') == 'Hi person!'

#%% example extensions
from spacy.tokens import Doc, Span, Token
nlp = spacy.load('en')

fruits = ['apple', 'pear', 'banana', 'orange', 'strawberry']
is_fruit_getter = lambda token: token.text in fruits
has_fruit_getter = lambda obj: any([t.text in fruits for t in obj])

Token.set_extension('is_fruit', getter=is_fruit_getter)
Doc.set_extension('has_fruit', getter=has_fruit_getter)
Span.set_extension('has_fruit', getter=has_fruit_getter)

doc = nlp(u"I have an apple and a melon")
assert doc[3]._.is_fruit      # get Token attributes
assert not doc[0]._.is_fruit
assert doc._.has_fruit        # get Doc attributes
assert doc[1:4]._.has_fruit   # get Span attributes


#%% similarity
doc1 = nlp(u"The labrador barked.")
doc2 = nlp(u"The labrador swam.")
doc3 = nlp(u"the labrador people live in canada.")

for doc in [doc1, doc2, doc3]:
    labrador = doc[1]
    dog = nlp(u"dog")
    print(labrador.similarity(dog))

#%%
doc1 = nlp(u"Paris is the largest city in France.")
doc2 = nlp(u"Vilnius is the capital of Lithuania.")
doc3 = nlp(u"An emu is a large bird.")

for doc in [doc1, doc2, doc3]:
    for other_doc in [doc1, doc2, doc3]:
        print(doc.similarity(other_doc))

#%% prune vectors
nlp = spacy.load('en_vectors_web_lg')
n_vectors = 105000  # number of vectors to keep
removed_words = nlp.vocab.prune_vectors(n_vectors)

assert len(nlp.vocab.vectors) <= n_vectors  # unique vectors have been pruned
assert nlp.vocab.vectors.n_keys > n_vectors  # but not the total entries

#%% set vectors for specific words in vocab
import spacy
nlp = spacy.load('en_vectors_web_lg')
from spacy.vocab import Vocab
import numpy
vector_data = {u'dog': numpy.random.uniform(-1, 1, (300,)),
               u'cat': numpy.random.uniform(-1, 1, (300,)),
               u'orange': numpy.random.uniform(-1, 1, (300,))}

vocab = Vocab()
for word, vector in vector_data.items():
    vocab.set_vector(word, vector)

