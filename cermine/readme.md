# on ubuntu in windows
pdf2htmlEX picf.pdf --optimize-text 1 # html that looks like original

# identify parts of the pdf on windows gitbash
java -cp cermine-impl-1.13-jar-with-dependencies.jar pl.edu.icm.cermine.ContentExtractor -path . -outputs "jats,text,zones,trueviz,images"
