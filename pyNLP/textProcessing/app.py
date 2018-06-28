import spacy
from pyquery import PyQuery as q
import os, re
# from preprocessText import removeStatsEtc
# get from text utils
nlp = spacy.load('en')

# %%
text = "This feature allows us to control for calendar effects."
doc = nlp(text)
noun_chunks = list(list(doc.sents)[0].noun_chunks);
noun_chunks = set([n.text for n in noun_chunks if bool(re.search('\s', n.text))])
for n in noun_chunks:
    text = text.replace(n, '<np>' + n + '</np>')

def readTextFromXmlFile():
    xmlFilePath = os.path.join(os.getcwd(), 'assets', 'picf.xml');
    with open(xmlFilePath, 'r', encoding='utf8') as f:
        qxml = q(f.read())
    qxml("p xref").replaceWith(lambda i, e: ' ' + qxml(e).text() + ' ')
    text = qxml("p:not(caption)")


def addNounPhraseAndSentenceTags(sentencesFromNLP):
    """
    puts a span around sentnces and <np> around noun phrases
    :param sentencesFromNLP:
    :return:
    """
    sentences = []
    for sentence in sentencesFromNLP:
        sentenceAsSpans = '<span>' + sentence.text + '</span>'
        noun_chunks = set([nc.text for nc in sentence.noun_chunks])
        for n in noun_chunks:
            sentenceAsSpans = sentenceAsSpans.replace(n, '<np>' + n + '</np>')
        sentences.append(sentenceAsSpans)
    return sentences

def addNLPTagsToPlainText(plainText: str):
    """
    :param qxml: PyQuery object, like $ in jquery
    """
    sentencesFromNLP = nlp(removeStatsEtc(plainText)).sents
    sentencesWithXMLTags = addNounPhraseAndSentenceTags(sentencesFromNLP)
    return sentencesWithXMLTags

def addNLPTagsToXML(*, xmlText: object, qxml: object):
    """
    :param xmlText: e.g. xmlText = qxml("p:not(caption)")
    :param qxml: PyQuery object, like $ in jquery
    """
    for paragraph in xmlText:
        sentencesFromNLP = nlp(removeStatsEtc(paragraph.text)).sents
        sentencesWithXMLTags = addNounPhraseAndSentenceTags(sentencesFromNLP)
        qxml(paragraph).html('\n' + ' '.join(sentencesWithXMLTags))  # qxml is like jquery
    return qxml


def writeXMLToDisk(qxml):
    """
    :param qxml: PyQuery object, like $ in jquery
    """
    with open(os.path.join(os.getcwd(), 'assets', 'picf_nounphrases.xml'), 'w', encoding='utf8') as f:
        f.write(qxml.html())

addNLPTagsToPlainText(text)
# %% maybe keywords -> filtered noun chunks for map starter?
# import nlp.textacy.keyterms
#
# tdoc = textacy.Doc(text, lang=en)
#
# terms = textacy.keyterms.sgrank(tdoc, n_keyterms=30, window_width=50, ngrams=(1, 2, 3, 4))
# terms = [t[0] for t in terms]
# terms = nlp(' '.join(terms))
