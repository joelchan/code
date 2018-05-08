import re
# import textacy


def removeStatsEtc(text):
    # text = textacy.preprocess.normalize_whitespace(text)
    text = re.sub('\n',' ', text)
    text = re.sub('[Ff]ig.','Fig', text)
    text = re.sub('[\[][^\]]*[^\]]*[\]]', '', text)# remove results in format [ * t( * ]
    text = re.sub('[\(\[][^\)^*\]]*[pP\s]:?[<=>][^\)]*[\)\]]','', text)# if has p values in [] or ()
    text = re.sub('\**?[pP]\s*?[<|=|>][\s]?[\d|\.]*','', text) # if has p values without [] or ()
    return text
