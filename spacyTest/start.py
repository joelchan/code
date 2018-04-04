from spacy import displacy
import spacy
nlp = spacy.load('en_core_web_lg')
import fitz

#%%
import sys

pdfName = 'Zhang_et_al-2014-Journal_of_the_Association_for_Information_Science_and_Technology.pdf'
pdfDir = 'E:\\GoogleSync\\pdfs'
ofile = "zhang.txt"

doc = fitz.open(pdfDir + '\\' + pdfName)
pages = len(doc)

pdfText = ''
for page in doc:
    pdfText = pdfText + page.getText()


# %%
text = u"""In Study 1, regardless of whether they anticipated a partner, participants had better performance 
if they annotated more about connections across documents. In Study 2, annotations that pointed to
 more connections across documents improved the performance of the second participant. Annotations
  that pointed to few connections across documents hurt performance, especially when people were
   more aware of their partners.""".replace('\n', '')
doc = nlp(pdfText.replace('\n', '').replace('-',' '))
nounChunks = set([chunk.text for chunk in doc.ents])
html = text
# for chunk in nounChunks:
#     print(chunk)

wordList = []
for word in doc:
    if word.pos_ in ['NOUN', 'PNOUN', 'VERB'] and not word.is_oov:
        wordList.append(word)


# get unique from object attribute
seen = set()
unique = [obj for obj in wordList if obj.lemma_ not in seen and not seen.add(obj.lemma_)]
table = [[w.lemma_, w.prob, w.pos_] for w in sorted(unique, key=lambda word_: word_.prob)]

# Doc.merge