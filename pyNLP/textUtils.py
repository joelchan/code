import html, re


def wt103RegexFixes(x):
    re1 = re.compile(r'  +')
    x = x.replace('#39;', "'").replace('amp;', '&').replace('#146;', "'") \
        .replace('nbsp;', ' ').replace('#36;', '$').replace('\\n', "\n") \
        .replace('quot;', "'") \
        .replace('<br />', "\n").replace('\\"', '"').replace('<unk>', 'u_n') \
        .replace(' @.@ ', '.').replace(' @-@ ', '-').replace('\\', ' \\ ')
    return re1.sub(' ', html.unescape(x))


def removeStatsFromText(text):
    # text = textacy.preprocess.normalize_whitespace(text)
    text = re.sub('\n', ' ', text)
    text = re.sub('[Ff]ig.', 'Fig', text)
    text = re.sub('[\[][^\]]*[^\]]*[\]]', '',
                  text)  # remove results in format [ * t( * ]
    text = re.sub('[\(\[][^\)^*\]]*[pP\s]:?[<=>][^\)]*[\)\]]', '',
                  text)  # if has p values in [] or ()
    text = re.sub('\**?[pP]\s*?[<|=|>][\s]?[\d|\.]*', '',
                  text)  # if has p values without [] or ()
    return text
