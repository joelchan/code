from spacy import displacy
import spacy
nlp = spacy.load('en_core_web_lg')
import os, re

#%%
filePath = os.path.join('E:\\code\\spacyTest', 'CiteSense.txt')
with open(filePath,'r', encoding='utf8') as f:
    fileText = f.read();
print(fileText)
#%%
text_noCitations = re.sub('\[(\d|,)+\]', '', fileText)
doc = nlp(text_noCitations)

wordList = []
for word in doc:
    if word.pos_ in ['NOUN', 'PNOUN', 'VERB']:
        wordList.append(word)


# get unique from object attribute
seen = set()
unique = [obj for obj in wordList if obj.lemma_ not in seen and not seen.add(obj.lemma_)]
_ = [print(w.lemma_, w.prob, w.pos_) for w in sorted(unique, key=lambda word_: word_.prob)]

# Doc.merge