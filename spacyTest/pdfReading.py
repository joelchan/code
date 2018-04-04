import fitz
import sys

pdfName = 'Zhang_et_al-2014-Journal_of_the_Association_for_Information_Science_and_Technology.pdf'
pdfDir = 'E:\\GoogleSync\\pdfs'
ofile = "zhang.txt"

doc = fitz.open(pdfDir + '\\' + pdfName)
pages = len(doc)

fout = open(ofile,"w")

for page in doc:
    text = page.getText()
    print(text)
    # fout.write(text.encode("utf-8"))

fout.close()