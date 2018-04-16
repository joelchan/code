from pyquery import PyQuery as q
import os, textacy, spacy
from spacy.tokens import Doc
from spacy_lookup import Entity
nlp = spacy.load('en_core_web_lg')

xmlFilePath = os.path.join(os.getcwd(), 'assets', 'picf.xml');
with open(xmlFilePath,'r', encoding='utf8') as f:
    qxml = q(f.read())

#%% preprocess textacy
text = qxml("p:not(caption)").text();
text = textacy.preprocess.preprocess_text(text,
    lowercase=True, no_numbers=False,
    no_urls=True, no_emails=True, no_contractions=True)
text = textacy.preprocess.remove_punct(text, marks='()[]<>=;:,\n')
text = textacy.preprocess.normalize_whitespace(text)

#%%
# entity = Entity(nlp, keywords_list=['cognitive function', 'cognitive control', 'fluid'], label='construct')
# nlp.add_pipe(entity, last=True, force=True)
doc = nlp(text)
#%%
[print(i.label_, i.text) for i in list(doc.ents)]

#%% maybe keywords -> filtered noun chunks for map starter?
phrases = [t for t in set([chunk.text for chunk in doc.noun_chunks])
 if 'cognitive' in t]
import re
def hasNumbers(inputString):
     return bool(re.search(r'\d', inputString))
phrases = [print(p) for p in phrases if not hasNumbers(p)]


