from pyquery import PyQuery as q
import os, textacy, spacy
from spacy.tokens import Doc
from spacy_lookup import Entity
import re
nlp = spacy.load('en_core_web_lg')
en = textacy.load_spacy('en_core_web_lg')

#%% preprocess textacy
xmlFilePath = os.path.join(os.getcwd(), 'assets', 'picf.xml');
with open(xmlFilePath,'r', encoding='utf8') as f:
    qxml = q(f.read())
qxml("p xref").replaceWith(lambda i, e: ' ' + qxml(e).text() + ' ')

text = qxml("p:not(caption)")


def removeStatsEtc(text):
    text = textacy.preprocess.normalize_whitespace(text)
    text = re.sub('\n',' ', text)
    text = re.sub('[Ff]ig.','Fig', text)
    text = re.sub('[\[][^\]]*[^\]]*[\]]', '', text)# remove results in format [ * t( * ]
    text = re.sub('[\(\[][^\)^*\]]*[pP\s]:?[<=>][^\)]*[\)\]]','', text)# if has p values in [] or ()
    text = re.sub('\**?[pP]\s*?[<|=|>][\s]?[\d|\.]*','', text) # if has p values without [] or ()
    return text

def getSentences(text):
    doc = nlp(removeStatsEtc(text))
    return doc.sents

for (i, p) in enumerate(text):
    sents = getSentences(p.text)
    sentencesAsSpans = ['<span>' + s.text + '</span>' for s in sents]
    print(i, p.text)
    qxml(p).html('\n' + ' '.join(sentencesAsSpans) )

with open(os.path.join(os.getcwd(), 'assets', 'picf_sentences.xml'),'w', encoding='utf8') as f:
    f.write(qxml.html())

#%% maybe keywords -> filtered noun chunks for map starter?
import textacy.keyterms
tdoc = textacy.Doc(text, lang=en)

terms = textacy.keyterms.sgrank(tdoc, n_keyterms=30, window_width=50, ngrams=(1,2,3,4))
terms = [t[0] for t in terms]
terms = nlp(' '.join(terms))


phrases = [t for t in set([chunk.text for chunk in doc.noun_chunks])
 if 'cognitive' in t]
def hasNumbers(inputString):
     return bool(re.search(r'\d', inputString))
phrases = [print(p) for p in phrases]


