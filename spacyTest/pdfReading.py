#%%
import fitz
import sys
import os

pdfName = 'povertyimpedescognitivefunction.pdf'
pdfDir = 'E:\\code\\spacyTest'
ofile = "povertyimpedescognitivefunction.html"

doc = fitz.open(pdfDir + '\\' + pdfName)
pages = len(doc)

pdfText = ''
for page in doc:
    pdfText = pdfText + page.getText('html')


my_file = os.path.join('E:\\code\\spacyTest', 'pdf.html')
with open(my_file,'w') as pdf:
    pdf.write(pdfText)
print(pdfText)